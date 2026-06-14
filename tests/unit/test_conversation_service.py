from app.services import ConversationService


def test_conversation_before_sales_turn_stays_general() -> None:
    service = ConversationService()

    reply = service.next_reply("мебель", 2)

    assert not reply.should_offer_products
    assert reply.text


def test_conversation_uses_dialogue_answer_before_sales_turn() -> None:
    service = ConversationService()

    reply = service.next_reply("море", 2, dialogue_answer="На море пригодятся очки с UV-защитой.")

    assert reply.text == "На море пригодятся очки с UV-защитой."
    assert not reply.should_offer_products


def test_conversation_offers_products_on_sixth_message() -> None:
    service = ConversationService()

    reply = service.next_reply("расскажи что-нибудь", 6)

    assert reply.should_offer_products
    assert "солнцезащитные очки" in reply.text
    assert "заказ" in reply.text
