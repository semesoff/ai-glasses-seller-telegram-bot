import csv
import logging
from pathlib import Path

from app.nlp.intent_classifier import Intent

logger = logging.getLogger(__name__)


class MLIntentClassifier:
    def __init__(self, dataset_path: Path, min_margin: float = -0.15) -> None:
        self.dataset_path = dataset_path
        self.min_margin = min_margin
        self._vectorizer = None
        self._classifier = None

    def _ensure_model(self) -> None:
        if self._classifier is not None:
            return
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.svm import LinearSVC
        except ImportError:
            logger.warning("sklearn_unavailable intent ML fallback disabled")
            return
        if not self.dataset_path.exists():
            logger.warning("intent_dataset_missing path=%s", self.dataset_path)
            return

        texts: list[str] = []
        labels: list[str] = []
        with self.dataset_path.open("r", encoding="utf-8", newline="") as file:
            reader = csv.DictReader(file)
            for row in reader:
                query = (row.get("query") or "").strip()
                intent = (row.get("intent") or "").strip()
                if query and intent in Intent.__members__:
                    texts.append(query.lower())
                    labels.append(intent)

        if len(set(labels)) < 2:
            logger.warning("intent_dataset_too_small path=%s", self.dataset_path)
            return

        vectorizer = TfidfVectorizer(analyzer="char", ngram_range=(3, 5), lowercase=True)
        classifier = LinearSVC()
        matrix = vectorizer.fit_transform(texts)
        classifier.fit(matrix, labels)
        self._vectorizer = vectorizer
        self._classifier = classifier

    def predict(self, text: str) -> Intent:
        self._ensure_model()
        if self._classifier is None or self._vectorizer is None:
            return Intent.UNKNOWN
        matrix = self._vectorizer.transform([text.lower().strip()])
        prediction = self._classifier.predict(matrix)[0]
        scores = self._classifier.decision_function(matrix)
        max_score = float(scores.max()) if hasattr(scores, "max") else 0.0
        if max_score < self.min_margin:
            return Intent.UNKNOWN
        try:
            return Intent(prediction)
        except ValueError:
            return Intent.UNKNOWN
