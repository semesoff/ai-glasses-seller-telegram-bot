import logging
import re
from dataclasses import dataclass

import httpx

from app.config import get_settings

logger = logging.getLogger(__name__)

CJK_RE = re.compile(r"[\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]")
CYRILLIC_RE = re.compile(r"[А-Яа-яЁё]")
LETTER_RE = re.compile(r"[A-Za-zА-Яа-яЁё]")


@dataclass(frozen=True)
class LLMReply:
    text: str
    available: bool = True


class LLMService:
    def __init__(self) -> None:
        self.settings = get_settings()

    def _build_system_prompt(self, dialog_count: int, strict: bool = False) -> str:
        sales_hint = ""
        if dialog_count >= 6:
            sales_hint = (
                "\nЭто 6-е или более позднее сообщение пользователя. Если это уместно, мягко свяжи тему "
                "с солнцезащитными очками и предложи посмотреть несколько моделей. Не дави и не звучи как реклама."
            )

        strict_hint = ""
        if strict:
            strict_hint = (
                " КРИТИЧЕСКИ ВАЖНО: отвечай только на русском языке. "
                "Не используй китайские, японские, корейские, английские или любые другие иностранные символы. "
                "Если не уверен, дай короткий нейтральный русский ответ."
            )

        return (
            "Ты Telegram-бот магазина очков, но сначала ты живой дружелюбный собеседник. "
            "Общайся естественно на любые бытовые, учебные, творческие и технические темы. "
            "Если пользователь пишет одно слово или случайный предмет вроде 'кот', 'кухня', 'мебель', "
            "воспринимай это как тему для разговора: задай простой уточняющий вопрос или дай короткую живую реакцию. "
            "Не называй сообщение странным и не выдумывай несуществующие магазины, бренды или факты. "
            "Отвечай по-русски, кратко: 1-3 предложения. "
            "Не говори, что ты языковая модель. "
            "До 6-го сообщения не продавай очки напрямую. "
            "После 6-го сообщения можешь мягко предложить солнцезащитные очки, если переход выглядит естественно."
            f"{strict_hint}"
            f"{sales_hint}"
        )

    def _is_valid_russian_reply(self, text: str) -> bool:
        if not text:
            return False
        if CJK_RE.search(text):
            return False
        letters = LETTER_RE.findall(text)
        if not letters:
            return True
        cyrillic = CYRILLIC_RE.findall(text)
        return len(cyrillic) / len(letters) >= 0.75

    async def _request_chat(
        self,
        user_text: str,
        history: list[dict[str, str]],
        dialog_count: int,
        *,
        strict: bool = False,
    ) -> str | None:
        system_prompt = self._build_system_prompt(dialog_count, strict=strict)
        messages = [{"role": "system", "content": system_prompt}, *history[-10:], {"role": "user", "content": user_text}]
        payload = {
            "model": self.settings.ollama_model,
            "messages": messages,
            "stream": False,
            "options": {"temperature": 0.2 if strict else 0.25, "top_p": 0.75, "num_predict": 130},
        }
        try:
            async with httpx.AsyncClient(timeout=45) as client:
                response = await client.post(f"{self.settings.ollama_base_url}/api/chat", json=payload)
                response.raise_for_status()
                data = response.json()
        except Exception as exc:
            logger.warning("llm_unavailable model=%s error=%s", self.settings.ollama_model, exc)
            return None

        return (data.get("message") or {}).get("content", "").strip()

    async def chat(self, user_text: str, history: list[dict[str, str]], dialog_count: int) -> LLMReply:
        if not self.settings.llm_enabled:
            return LLMReply(text="", available=False)

        text = await self._request_chat(user_text, history, dialog_count)
        if text and self._is_valid_russian_reply(text):
            logger.info('llm_reply dialog_count=%s text="%s"', dialog_count, " ".join(text.split())[:500])
            return LLMReply(text=text, available=True)

        if text:
            logger.warning('llm_invalid_reply dialog_count=%s text="%s"', dialog_count, " ".join(text.split())[:500])

        retry_text = await self._request_chat(user_text, history, dialog_count, strict=True)
        if retry_text and self._is_valid_russian_reply(retry_text):
            logger.info('llm_reply_retry dialog_count=%s text="%s"', dialog_count, " ".join(retry_text.split())[:500])
            return LLMReply(text=retry_text, available=True)

        if retry_text:
            logger.warning(
                'llm_invalid_retry dialog_count=%s text="%s"',
                dialog_count,
                " ".join(retry_text.split())[:500],
            )
        return LLMReply(text="", available=False)
