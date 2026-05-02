from decimal import Decimal

from django.contrib import messages
from django.core import signing
from django.core.signing import BadSignature
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

from .forms import DocumentFillForm
from .models import DocumentTemplate, GeneratedDocument


def _jsonify(value):
    if isinstance(value, dict):
        return {key: _jsonify(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_jsonify(item) for item in value]
    if isinstance(value, tuple):
        return [_jsonify(item) for item in value]
    if isinstance(value, Decimal):
        return str(value)
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return value


def index(request):
    templates = DocumentTemplate.objects.all()
    return render(
        request,
        "documents/index.html",
        {
            "title": "Документы",
            "templates": templates,
        },
    )


def detail(request, slug):
    template = get_object_or_404(DocumentTemplate, slug=slug)
    form = DocumentFillForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        rendered_text = template.render(form.cleaned_data)
        data = _jsonify(form.cleaned_data)

        if request.user.is_authenticated:
            document = GeneratedDocument.objects.create(
                user=request.user,
                template=template,
                input_data=data,
                rendered_text=rendered_text,
            )
            return redirect(f"{reverse('documents:generated')}?document_id={document.pk}")

        token = signing.dumps({"template": template.slug, "data": data})
        return redirect(f"{reverse('documents:generated')}?token={token}")

    if request.method == "POST":
        messages.error(request, "Проверьте поля формы и попробуйте еще раз.")

    return render(
        request,
        "documents/detail.html",
        {
            "title": template.title,
            "template": template,
            "form": form,
        },
    )


def generated(request):
    document = None
    template = None
    rendered_text = ""
    download_token = request.GET.get("token")
    document_id = request.GET.get("document_id")

    if document_id:
        if request.user.is_authenticated:
            document = get_object_or_404(GeneratedDocument, pk=document_id, user=request.user)
        else:
            raise Http404("Документ не найден")
        template = document.template
        rendered_text = document.rendered_text
    elif download_token:
        try:
            payload = signing.loads(download_token, max_age=60 * 60 * 24 * 7)
        except BadSignature as exc:
            raise Http404("Документ не найден") from exc
        template = get_object_or_404(DocumentTemplate, slug=payload["template"])
        rendered_text = template.render(payload["data"])
    else:
        raise Http404("Документ не найден")

    if request.GET.get("download") == "1":
        filename = document.filename if document else f"{template.slug}.txt"
        response = HttpResponse(rendered_text, content_type="text/plain; charset=utf-8")
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        return response

    return render(
        request,
        "documents/generated.html",
        {
            "title": f"Готовый документ — {template.title}",
            "template": template,
            "rendered_text": rendered_text,
            "document": document,
            "download_query": f"?document_id={document.pk}" if document else f"?token={download_token}",
            "created_at": document.created_at if document else timezone.now(),
        },
    )