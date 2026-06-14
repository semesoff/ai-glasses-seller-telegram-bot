from pathlib import Path

from app.services import DialogueService


def test_dialogue_service_finds_close_answer(tmp_path: Path) -> None:
    dataset = tmp_path / "dialogues.txt"
    dataset.write_text(
        "Скоро отпуск\nДля отпуска пригодятся солнцезащитные очки.\n\n"
        "Кухня\nКухня часто задает настроение дому.\n",
        encoding="utf-8",
    )
    service = DialogueService(dataset_path=dataset)

    assert service.find_answer("у меня скоро отпуск") == "Для отпуска пригодятся солнцезащитные очки."
