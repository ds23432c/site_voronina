import uuid

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.urls import reverse

from .forms import ChatMessageForm
from .models import ChatMessage, ChatSession
from .services import generate_reply


def _get_chat_session(request):
    session_id = request.session.get("chat_session_id")

    if request.user.is_authenticated:
        if session_id:
            chat_session = ChatSession.objects.filter(session_id=session_id).first()
            if chat_session:
                if chat_session.user_id != request.user.id:
                    chat_session.user = request.user
                    chat_session.save(update_fields=["user"])
                return chat_session

        chat_session, _ = ChatSession.objects.get_or_create(
            user=request.user,
            defaults={"session_id": uuid.uuid4()},
        )
        request.session["chat_session_id"] = str(chat_session.session_id)
        return chat_session

    if session_id:
        chat_session = ChatSession.objects.filter(session_id=session_id).first()
        if chat_session:
            return chat_session

    chat_session = ChatSession.objects.create()
    request.session["chat_session_id"] = str(chat_session.session_id)
    return chat_session


def _conversation_for_api(chat_session):
    messages = list(chat_session.messages.order_by("created_at").values("role", "content"))[-20:]
    return [{"role": item["role"], "content": item["content"]} for item in messages if item["role"] in {"user", "assistant"}]


def index(request):
    chat_session = _get_chat_session(request)
    form = ChatMessageForm()
    messages = chat_session.messages.order_by("created_at")

    return render(
        request,
        "chat/index.html",
        {
            "title": "Чат с БухПомощником",
            "form": form,
            "chat_session": chat_session,
            "messages": messages,
            "api_url": reverse("chat:api_send"),
            "history_url": reverse("chat:history") if request.user.is_authenticated else None,
        },
    )


@login_required
def history(request):
    chat_session = _get_chat_session(request)
    messages = chat_session.messages.order_by("created_at")
    return render(
        request,
        "chat/history.html",
        {
            "title": "История чата",
            "chat_session": chat_session,
            "messages": messages,
        },
    )


def send_message_api(request):
    if request.method != "POST":
        return JsonResponse({"ok": False, "error": "Метод не поддерживается."}, status=405)

    form = ChatMessageForm(request.POST)
    if not form.is_valid():
        return JsonResponse({"ok": False, "errors": form.errors}, status=400)

    chat_session = _get_chat_session(request)
    user_message = ChatMessage.objects.create(
        session=chat_session,
        role=ChatMessage.Role.USER,
        content=form.cleaned_data["message"],
    )

    payload = _conversation_for_api(chat_session)
    reply_text = generate_reply(payload)

    assistant_message = ChatMessage.objects.create(
        session=chat_session,
        role=ChatMessage.Role.ASSISTANT,
        content=reply_text,
    )
    chat_session.save()

    return JsonResponse(
        {
            "ok": True,
            "session_id": str(chat_session.session_id),
            "reply": assistant_message.content,
            "reply_created_at": assistant_message.created_at.isoformat(),
            "user_message": user_message.content,
        }
    )