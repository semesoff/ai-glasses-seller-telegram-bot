from difflib import SequenceMatcher
from pathlib import Path

from app.config import get_settings


class DialogueService:
    def __init__(self, dataset_path: Path | None = None, min_similarity: float = 0.48) -> None:
        self.dataset_path = dataset_path or get_settings().dialogues_txt
        self.min_similarity = min_similarity
        self._pairs: list[tuple[str, str]] | None = None

    def _load_pairs(self) -> list[tuple[str, str]]:
        if self._pairs is not None:
            return self._pairs
        if not self.dataset_path.exists():
            self._pairs = []
            return self._pairs
        lines = [line.strip() for line in self.dataset_path.read_text(encoding="utf-8").splitlines()]
        meaningful = [line for line in lines if line]
        pairs: list[tuple[str, str]] = []
        for index in range(0, len(meaningful) - 1, 2):
            pairs.append((meaningful[index].lower(), meaningful[index + 1]))
        self._pairs = pairs
        return pairs

    def find_answer(self, text: str) -> str | None:
        query = text.lower().strip()
        if not query:
            return None
        best_score = 0.0
        best_answer: str | None = None
        for question, answer in self._load_pairs():
            score = SequenceMatcher(None, query, question).ratio()
            if question in query or query in question:
                score = max(score, 0.8)
            if score > best_score:
                best_score = score
                best_answer = answer
        return best_answer if best_score >= self.min_similarity else None
