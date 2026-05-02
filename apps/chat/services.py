import uuid

import httpx
from django.conf import settings


SYSTEM_PROMPT_RU = (
    "Ты — БухПомощник, вежливый и профессиональный ассистент по бухгалтерии, налогам и документообороту "
    "в России. Отвечай по-русски, кратко и по делу, с учетом действующего законодательства РФ. "
    "Если данных недостаточно, задай уточняющий вопрос. Не выдумывай нормы права, а аккуратно сообщай о "
    "необходимости проверки актуальной редакции закона или консультации специалиста. По возможности "
    "структурируй ответ списком и указывай практический следующий шаг."
)


def _get_access_token() -> str:
    if not settings.GIGACHAT_API_KEY:
        raise ValueError("GIGACHAT_API_KEY is not configured.")

    response = httpx.post(
        settings.GIGACHAT_TOKEN_URL,
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
            "RqUID": str(uuid.uuid4()),
            "Authorization": f"Basic {settings.GIGACHAT_API_KEY}",
        },
        data={"scope": settings.GIGACHAT_SCOPE},
        timeout=30.0,
        verify=False,
    )
    response.raise_for_status()

    payload = response.json()
    access_token = payload.get("access_token")
    if not access_token:
        raise ValueError("GigaChat token response does not contain access_token.")

    return access_token


def _extract_reply(payload: dict) -> str:
    choices = payload.get("choices") or []
    if not choices:
        return ""

    message = choices[0].get("message") or {}
    for key in ("content", "text"):
        content = message.get(key)
        if isinstance(content, str) and content.strip():
            return content.strip()

    return ""


def generate_reply(messages: list[dict]) -> str:
    if not messages:
        return "Опишите вопрос подробнее, и я помогу с расчетом, отчетностью или документом."

    try:
        access_token = _get_access_token()
        response = httpx.post(
            f"{settings.GIGACHAT_BASE_URL.rstrip('/')}/v1/chat/completions",
            headers={
                "Accept": "application/json",
                "Authorization": f"Bearer {access_token}",
            },
            json={
                "model": settings.GIGACHAT_MODEL,
                "messages": messages,
                "temperature": 0.3,
                "max_tokens": 800,
            },
            timeout=60.0,
            verify=False,
        )
        response.raise_for_status()

        reply_text = _extract_reply(response.json())
        return reply_text or "Не удалось сформировать ответ. Попробуйте сформулировать вопрос иначе."
    except (httpx.HTTPError, ValueError):
        return "Сервис ИИ временно недоступен. Попробуйте повторить запрос позже."
