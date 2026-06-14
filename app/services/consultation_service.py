import re
from dataclasses import dataclass
from typing import Any


GOAL_LABELS = {
    "everyday": "каждый день",
    "driving": "вождение",
    "beach": "пляж и отдых",
    "gift": "подарок",
    "fashion": "стильный образ",
}
STYLE_LABELS = {
    "classic": "классика",
    "sport": "спорт",
    "premium": "премиум",
    "bright": "яркий образ",
    "minimal": "минимализм",
}
SHAPE_LABELS = {
    "aviator": "авиаторы",
    "round": "круглые",
    "square": "квадратные",
    "rectangular": "прямоугольные",
    "any": "подберу сам",
}


@dataclass(frozen=True)
class ConsultationRecommendation:
    filters: dict[str, Any]
    explanation: str


class ConsultationService:
    trigger_words = (
        "подбери",
        "подобрать",
        "помоги выбрать",
        "посоветуй",
        "консультация",
        "стилист",
        "какие очки",
    )

    def should_start(self, text: str) -> bool:
        lowered = text.lower()
        return any(word in lowered for word in self.trigger_words)

    def normalize_budget(self, value: str) -> int | None:
        if value == "any":
            return None
        match = re.search(r"\d{3,6}", value)
        return int(match.group(0)) if match else None

    def defaults_for_shape(self, goal: str, style: str) -> str:
        if goal == "driving" or style == "classic":
            return "aviator"
        if style == "sport":
            return "rectangular"
        if style == "bright":
            return "round"
        return "square"

    def build_filters(self, data: dict[str, Any], page: int = 1) -> dict[str, Any]:
        shape = data.get("shape_preference") or "any"
        if shape == "any":
            shape = self.defaults_for_shape(data.get("goal", "everyday"), data.get("style", "classic"))
        filters: dict[str, Any] = {
            "type": "sunglasses",
            "gender": data.get("gender", "unisex"),
            "shape": shape,
            "page": page,
        }
        budget = self.normalize_budget(str(data.get("budget", "any")))
        if budget:
            filters["max_price"] = budget
        return filters

    def recommendation(self, data: dict[str, Any], page: int = 1) -> ConsultationRecommendation:
        filters = self.build_filters(data, page=page)
        goal = GOAL_LABELS.get(data.get("goal", "everyday"), "каждый день")
        style = STYLE_LABELS.get(data.get("style", "classic"), "классика")
        shape = SHAPE_LABELS.get(filters["shape"], filters["shape"])
        budget = filters.get("max_price")
        budget_text = f"в пределах {budget} рублей" if budget else "без жесткого ограничения по бюджету"
        explanation = (
            f"Я бы смотрел в сторону формы «{shape}»: она хорошо работает под задачу «{goal}» "
            f"и стиль «{style}». Ниже варианты {budget_text}. "
            "Если модель нравится, можно сразу оформить заказ."
        )
        return ConsultationRecommendation(filters=filters, explanation=explanation)

