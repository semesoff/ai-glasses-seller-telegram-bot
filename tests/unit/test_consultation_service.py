from app.services import ConsultationService


def test_consultation_trigger_phrases() -> None:
    service = ConsultationService()

    assert service.should_start("Помоги выбрать очки")
    assert service.should_start("Посоветуй солнцезащитные очки")
    assert not service.should_start("Есть доставка?")


def test_budget_is_converted_to_max_price() -> None:
    service = ConsultationService()

    assert service.normalize_budget("до 7000 рублей") == 7000
    assert service.normalize_budget("10000") == 10000
    assert service.normalize_budget("any") is None


def test_unknown_shape_uses_stylist_default() -> None:
    service = ConsultationService()

    filters = service.build_filters({
        "goal": "driving",
        "gender": "male",
        "style": "minimal",
        "shape_preference": "any",
        "budget": "7000",
    })

    assert filters["type"] == "sunglasses"
    assert filters["gender"] == "male"
    assert filters["shape"] == "aviator"
    assert filters["max_price"] == 7000


def test_recommendation_contains_filters_and_explanation() -> None:
    service = ConsultationService()

    recommendation = service.recommendation({
        "goal": "fashion",
        "gender": "female",
        "style": "bright",
        "shape_preference": "round",
        "budget": "5000",
    })

    assert recommendation.filters["shape"] == "round"
    assert recommendation.filters["max_price"] == 5000
    assert "стильный образ" in recommendation.explanation
    assert "Купить" not in recommendation.explanation

