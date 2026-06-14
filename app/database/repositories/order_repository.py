from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database.models import Order, OrderStatus


class OrderRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, telegram_id: int, product_id: int, phone: str, address: str) -> Order:
        order = Order(telegram_id=telegram_id, product_id=product_id, phone=phone, address=address)
        self.session.add(order)
        await self.session.commit()
        await self.session.refresh(order)
        return order

    async def get_by_id(self, order_id: int) -> Order | None:
        return await self.session.get(Order, order_id)

    async def get_by_telegram_id(self, telegram_id: int, limit: int = 10) -> list[Order]:
        stmt = (
            select(Order)
            .options(selectinload(Order.product))
            .where(Order.telegram_id == telegram_id)
            .order_by(Order.created_at.desc(), Order.id.desc())
            .limit(limit)
        )
        return list((await self.session.scalars(stmt)).all())

    async def update_status(self, order_id: int, status: OrderStatus) -> Order | None:
        order = await self.get_by_id(order_id)
        if order is None:
            return None
        order.status = status
        await self.session.commit()
        await self.session.refresh(order)
        return order
