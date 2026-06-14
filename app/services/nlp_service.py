from dataclasses import dataclass
from typing import Any

from app.config import get_settings
from app.nlp import Intent, classify_intent, extract_entities
from app.nlp.ml_intent_classifier import MLIntentClassifier


@dataclass(frozen=True)
class NLPResult:
    intent: Intent
    entities: dict[str, Any]


class NLPService:
    def __init__(self, ml_classifier: MLIntentClassifier | None = None) -> None:
        self.ml_classifier = ml_classifier or MLIntentClassifier(get_settings().intents_csv)

    def analyze(self, text: str) -> NLPResult:
        entities = extract_entities(text)
        rule_intent = classify_intent(text)
        if rule_intent != Intent.UNKNOWN:
            return NLPResult(intent=rule_intent, entities=entities)

        ml_intent = self.ml_classifier.predict(text)
        if ml_intent in {Intent.SEARCH_PRODUCT, Intent.CREATE_ORDER} and len(entities) <= 1:
            ml_intent = Intent.UNKNOWN
        return NLPResult(intent=ml_intent, entities=entities)
