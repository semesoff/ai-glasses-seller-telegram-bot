import asyncio
import logging
import tempfile
from pathlib import Path

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile, Message

from app.bot.handlers.text import process_text_message
from app.services import (
    ConsultationService,
    ConversationService,
    DialogueService,
    LLMService,
    NLPService,
    OrderService,
    ProductService,
    VoiceService,
)

router = Router()
logger = logging.getLogger(__name__)


@router.message(F.voice)
async def voice_message(
    message: Message,
    state: FSMContext,
    product_service: ProductService,
    order_service: OrderService,
    nlp_service: NLPService,
    consultation_service: ConsultationService,
    conversation_service: ConversationService,
    dialogue_service: DialogueService,
    llm_service: LLMService,
    voice_service: VoiceService,
) -> None:
    if not message.voice:
        return
    if not voice_service.available():
        await message.answer(
            "Голосовое распознавание пока недоступно: не найдена русская модель Vosk. "
            "Напишите команду текстом или добавьте модель и задайте VOSK_MODEL_PATH."
        )
        return

    with tempfile.TemporaryDirectory(prefix="glasses_voice_") as tmp:
        tmp_dir = Path(tmp)
        ogg_path = tmp_dir / "voice.ogg"
        file = await message.bot.get_file(message.voice.file_id)
        await message.bot.download_file(file.file_path, destination=ogg_path)

        try:
            recognized_text = await asyncio.to_thread(voice_service.transcribe, ogg_path)
        except Exception as exc:
            logger.warning("voice_transcription_failed error=%s", exc)
            await message.answer(
                "Не получилось распознать голосовое сообщение. Попробуйте ещё раз или напишите текстом."
            )
            return

        if not recognized_text:
            await message.answer(
                "Я не разобрал голосовое сообщение. Попробуйте сказать короче или написать текстом."
            )
            return

        telegram_id = message.from_user.id if message.from_user else None
        logger.info('voice_transcribed telegram_id=%s text="%s"', telegram_id, recognized_text)
        result = await process_text_message(
            message=message,
            state=state,
            text=recognized_text,
            product_service=product_service,
            order_service=order_service,
            nlp_service=nlp_service,
            consultation_service=consultation_service,
            conversation_service=conversation_service,
            dialogue_service=dialogue_service,
            llm_service=llm_service,
            voice_mode=True,
        )

        spoken_reply = voice_service.prepare_spoken_reply(
            result.spoken_text or "Я обработал голосовое сообщение и отправил ответ в чат."
        )
        logger.info('voice_reply telegram_id=%s text="%s"', telegram_id, spoken_reply)
        voice_reply = await asyncio.to_thread(
            voice_service.synthesize,
            spoken_reply,
            tmp_dir,
        )
        if voice_reply:
            await message.answer_voice(FSInputFile(voice_reply))
        elif not result.visual_sent:
            await message.answer(result.spoken_text or "Ответ готов, но голосовой синтез сейчас недоступен.")
