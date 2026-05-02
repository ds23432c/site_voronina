import logging
import uuid

import httpx
from django.conf import settings


logger = logging.getLogger(__name__)

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

    try:
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
    except httpx.HTTPError:
        logger.exception("Failed to get GigaChat access token")
        raise

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
        client_id = settings.GIGACHAT_CLIENT_ID.strip() or str(uuid.uuid5(uuid.NAMESPACE_DNS, settings.SITE_NAME))

        response = httpx.post(
            f"{settings.GIGACHAT_BASE_URL.rstrip('/')}/v1/chat/completions",
            headers={
                "Accept": "application/json",
                "Authorization": f"Bearer {access_token}",
                "X-Client-ID": client_id,
                "X-Request-ID": str(uuid.uuid4()),
                "X-Session-ID": str(uuid.uuid4()),
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
    except httpx.HTTPStatusError as exc:
        logger.exception(
            "GigaChat HTTP error: status=%s body=%s",
            exc.response.status_code,
            exc.response.text,
        )
        if getattr(settings, "DEBUG", False):
            return f"GigaChat HTTP error: status={exc.response.status_code} body={exc.response.text}"
        if exc.response.status_code in {401, 403}:
            return "Не удалось авторизоваться в GigaChat. Проверьте GIGACHAT_API_KEY и GIGACHAT_CLIENT_ID."
        if exc.response.status_code == 429:
            return "GigaChat временно ограничил запросы. Попробуйте позже."
        return "Сервис ИИ временно недоступен. Попробуйте повторить запрос позже."
    except httpx.RequestError as exc:
        logger.exception("GigaChat request failed: %s", exc)
        if getattr(settings, "DEBUG", False):
            return f"GigaChat request failed: {exc}"
        return "Сервис ИИ временно недоступен. Попробуйте повторить запрос позже."
    except ValueError as exc:
        logger.exception("GigaChat configuration error: %s", exc)
        if getattr(settings, "DEBUG", False):
            return f"GigaChat configuration error: {exc}"
        return "Сервис ИИ временно недоступен. Попробуйте повторить запрос позже."
