from html import escape

from aiogram import F, Router
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.bot.formatting import _money
from app.bot.keyboards import main_menu
from app.bot.states import OrderStates
from app.database.models import Order, OrderStatus, Product
from app.services import OrderService, ProductService

router = Router()

ORDER_STATUS_LABELS = {
    OrderStatus.NEW: "Новый",
    OrderStatus.CONFIRMED: "Подтверждён",
    OrderStatus.DELIVERING: "Передан в доставку",
    OrderStatus.COMPLETED: "Завершён",
}
ORDER_STATUS_EXPLANATIONS = {
    OrderStatus.NEW: "Мы получили заявку. Менеджер свяжется с вами, чтобы подтвердить наличие и детали доставки.",
    OrderStatus.CONFIRMED: "Заказ подтверждён и готовится к отправке.",
    OrderStatus.DELIVERING: "Заказ уже в доставке.",
    OrderStatus.COMPLETED: "Заказ завершён.",
}


def _product_title(product: Product | None, product_id: int | None = None) -> str:
    if product is None:
        return f"товар #{product_id}" if product_id else "выбранный товар"
    return f"{product.brand} — {product.name}"


def _format_order(order: Order) -> str:
    status = ORDER_STATUS_LABELS.get(order.status, str(order.status))
    explanation = ORDER_STATUS_EXPLANATIONS.get(order.status, "")
    product_title = _product_title(order.product, order.product_id)
    return (
        f"<b>Заказ №{order.id}</b>\n"
        f"Товар: <b>{escape(product_title)}</b>\n"
        f"Статус: <b>{escape(status)}</b>\n"
        f"{escape(explanation)}"
    )


async def ask_phone_for_product(
    message: Message,
    state: FSMContext,
    product_id: int,
    product_service: ProductService,
) -> None:
    product = await product_service.get_product(product_id)
    if product is None:
        await state.clear()
        await message.answer("Товар с таким ID не найден. Откройте /catalog и попробуйте снова.")
        return

    await state.update_data(product_id=product_id, product_title=_product_title(product), product_price=str(product.price))
    await state.set_state(OrderStates.phone)
    await message.answer(
        "Отлично, бронируем:\n"
        f"<b>{escape(_product_title(product))}</b>\n"
        f"Цена: <b>{escape(_money(product.price))}</b>\n\n"
        "Введите номер телефона для связи.",
        parse_mode=ParseMode.HTML,
    )


@router.message(Command("orders"))
async def my_orders_command(message: Message, state: FSMContext, order_service: OrderService) -> None:
    await state.clear()
    telegram_id = message.from_user.id if message.from_user else 0
    orders = await order_service.get_user_orders(telegram_id)
    if not orders:
        await message.answer(
            "У вас пока нет заказов. Можно открыть каталог или попросить меня подобрать очки.",
            reply_markup=main_menu(),
        )
        return
    await message.answer(
        "Ваши последние заказы:\n\n" + "\n\n".join(_format_order(order) for order in orders),
        parse_mode=ParseMode.HTML,
        reply_markup=main_menu(),
    )


@router.message(F.text.lower().in_({"мои заказы", "мой заказ", "заказы"}))
async def my_orders_button(message: Message, state: FSMContext, order_service: OrderService) -> None:
    await my_orders_command(message, state, order_service)


@router.message(Command("order"))
async def order_command(message: Message, state: FSMContext) -> None:
    await state.set_state(OrderStates.product_id)
    await message.answer(
        "Введите номер товара из каталога, который хотите заказать. "
        "Если хотите посмотреть уже созданные заказы, нажмите «Мои заказы» или отправьте /orders."
    )


@router.message(F.text.lower() == "оформить заказ")
async def order_button(message: Message, state: FSMContext) -> None:
    await order_command(message, state)


@router.message(OrderStates.product_id)
async def product_selected(message: Message, state: FSMContext, product_service: ProductService) -> None:
    if not message.text or not message.text.strip().isdigit():
        await message.answer("Введите числовой номер товара из каталога или нажмите «Мои заказы».")
        return
    await ask_phone_for_product(message, state, int(message.text.strip()), product_service)


@router.message(OrderStates.phone)
async def phone_entered(message: Message, state: FSMContext) -> None:
    if not message.text or len(message.text.strip()) < 7:
        await message.answer("Введите корректный номер телефона.")
        return
    await state.update_data(phone=message.text.strip())
    await state.set_state(OrderStates.address)
    await message.answer("Введите адрес доставки.")


@router.message(OrderStates.address)
async def address_entered(message: Message, state: FSMContext) -> None:
    if not message.text or len(message.text.strip()) < 5:
        await message.answer("Введите полный адрес доставки.")
        return
    await state.update_data(address=message.text.strip())
    data = await state.get_data()
    await state.set_state(OrderStates.confirmation)
    await message.answer(
        "Проверьте заказ:\n\n"
        f"Товар: <b>{escape(data.get('product_title', 'выбранный товар'))}</b>\n"
        f"Телефон: <b>{escape(data['phone'])}</b>\n"
        f"Адрес: <b>{escape(data['address'])}</b>\n\n"
        "Если всё верно, напишите «Да». Если передумали, напишите «Нет».",
        parse_mode=ParseMode.HTML,
    )


@router.message(OrderStates.confirmation)
async def order_confirmed(message: Message, state: FSMContext, order_service: OrderService) -> None:
    if not message.text or message.text.lower().strip() not in {"да", "yes", "y", "конечно", "верно", "подтверждаю"}:
        await state.clear()
        await message.answer("Заказ отменён.", reply_markup=main_menu())
        return
    data = await state.get_data()
    try:
        order = await order_service.create_order(
            telegram_id=message.from_user.id if message.from_user else 0,
            product_id=data["product_id"],
            phone=data["phone"],
            address=data["address"],
        )
    except ValueError:
        await state.clear()
        await message.answer("Товар не найден. Откройте /catalog и попробуйте снова.", reply_markup=main_menu())
        return
    await state.clear()
    await message.answer(
        f"Заказ №{order.id} создан.\n\n"
        f"Товар: <b>{escape(data.get('product_title', 'выбранный товар'))}</b>\n"
        f"Статус: <b>{ORDER_STATUS_LABELS[order.status]}</b>\n"
        f"{ORDER_STATUS_EXPLANATIONS[order.status]}\n\n"
        "Посмотреть свои заказы можно кнопкой «Мои заказы» или командой /orders.",
        parse_mode=ParseMode.HTML,
        reply_markup=main_menu(),
    )
