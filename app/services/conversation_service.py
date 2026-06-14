from dataclasses import dataclass


@dataclass(frozen=True)
class ConversationReply:
    text: str
    should_offer_products: bool = False


class ConversationService:
    sales_turn = 6

    def next_reply(self, user_text: str, message_count: int, dialogue_answer: str | None = None) -> ConversationReply:
        if message_count >= self.sales_turn:
            return ConversationReply(
                text=(
                    "Кстати, раз уж мы разговорились, предложу практичную мысль: хорошие солнцезащитные очки "
                    "часто оказываются той самой деталью, которая каждый день делает комфортнее. "
                    "Покажу несколько универсальных вариантов — если что-то понравится, можно сразу оформить заказ."
                ),
                should_offer_products=True,
            )

        if dialogue_answer:
            return ConversationReply(text=dialogue_answer)

        variants = [
            "Интересная тема. Расскажите чуть подробнее, что именно в этом зацепило?",
            "Понял. А если выбрать главное, что здесь важнее: удобство, внешний вид или практичность?",
            "Звучит как бытовая, но вполне живая история. Что с этим хотите сделать дальше?",
            "Я с вами. Давайте развернём: это больше про проблему, идею или просто мысль вслух?",
            "Люблю такие внезапные темы. Что первое приходит в голову, когда вы об этом думаете?",
        ]
        return ConversationReply(text=variants[(message_count - 1) % len(variants)])
