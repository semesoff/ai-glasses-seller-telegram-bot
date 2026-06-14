from app.services import LLMService


def test_llm_service_can_be_created() -> None:
    service = LLMService()

    assert service.settings.ollama_model


def test_llm_service_rejects_cjk_garbage() -> None:
    service = LLMService()

    assert not service._is_valid_russian_reply("А ты сфотографируешь вид на窗外的好天气?")


def test_llm_service_accepts_russian_reply() -> None:
    service = LLMService()

    assert service._is_valid_russian_reply("Здорово! У меня всё хорошо. А как проходит твой день?")
