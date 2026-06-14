from pathlib import Path

import pytest

from app.services import VoiceService


def test_voice_service_reports_missing_model(tmp_path: Path) -> None:
    service = VoiceService(model_path=tmp_path / "missing-model")

    assert not service.available()
    with pytest.raises(RuntimeError, match="Vosk model is not available"):
        service._load_model()


def test_prepare_spoken_reply_strips_markup_and_shortens() -> None:
    service = VoiceService()
    text = (
        "<b>Ray Ban — Aviator</b>\n"
        "Цена: <b>7 000 руб.</b>\n"
        "Особенности: металлическая оправа.\n"
        "Если модель понравилась, нажмите кнопку с её названием ниже. "
        "Дополнительное очень длинное описание не должно полностью уходить в голосовой ответ."
    )

    spoken = service.prepare_spoken_reply(text)

    assert "<b>" not in spoken
    assert "*" not in spoken
    assert "Ray Ban" in spoken
    assert len(spoken) <= 250


def test_voice_handler_does_not_send_transcription_debug_text() -> None:
    handler_source = Path("app/bot/handlers/voice.py").read_text(encoding="utf-8")

    assert "Я распознал:" not in handler_source
    assert "распознал голосовую команду" not in handler_source
