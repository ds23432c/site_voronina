import anthropic
from django.conf import settings

client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)

SYSTEM_PROMPT_RU = (
    "Ты — БухПомощник, вежливый и профессиональный ассистент по бухгалтерии, налогам и документообороту "
    "в России. Отвечай по-русски, кратко и по делу, с учетом действующего законодательства РФ. "
    "Если данных недостаточно, задай уточняющий вопрос. Не выдумывай нормы права, а аккуратно сообщай о "
    "необходимости проверки актуальной редакции закона или консультации специалиста. По возможности "
    "структурируй ответ списком и указывай практический следующий шаг."
)


def generate_reply(messages: list[dict]) -> str:
    if not messages:
        return "Опишите вопрос подробнее, и я помогу с расчетом, отчетностью или документом."

    try:
        response = client.messages.create(
            model=getattr(settings, "ANTHROPIC_MODEL", "claude-3-haiku-20240307"),
            max_tokens=800,
            temperature=0.3,
            system=SYSTEM_PROMPT_RU,
            messages=messages,
        )
        parts = []
        for item in getattr(response, "content", []):
            text = getattr(item, "text", None)
            if text:
                parts.append(text)
        return "\n".join(parts).strip() or "Не удалось сформировать ответ. Попробуйте сформулировать вопрос иначе."
    except Exception:
        return "Сервис ИИ временно недоступен. Попробуйте повторить запрос позже."