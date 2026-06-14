from decimal import Decimal
from typing import Any

from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Product


class ProductRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(self, limit: int = 10, offset: int = 0) -> list[Product]:
        stmt = select(Product).order_by(Product.id).limit(limit).offset(offset)
        return list((await self.session.scalars(stmt)).all())

    async def get_by_id(self, product_id: int) -> Product | None:
        return await self.session.get(Product, product_id)

    async def count(self) -> int:
        return await self.session.scalar(select(func.count(Product.id))) or 0

    async def find_by_filters(self, filters: dict[str, Any], limit: int = 10, offset: int = 0) -> list[Product]:
        stmt: Select[tuple[Product]] = select(Product)
        for field in ("type", "gender", "shape", "color", "frame_material"):
            value = filters.get(field)
            if value:
                stmt = stmt.where(getattr(Product, field) == value)
        if brand := filters.get("brand"):
            stmt = stmt.where(Product.brand.ilike(f"%{brand}%"))
        if max_price := filters.get("max_price"):
            stmt = stmt.where(Product.price <= Decimal(str(max_price)))
        stmt = stmt.order_by(Product.rating.desc().nullslast(), Product.reviews_count.desc()).limit(limit).offset(offset)
        return list((await self.session.scalars(stmt)).all())

    async def bulk_insert(self, rows: list[dict[str, Any]]) -> None:
        for row in rows:
            self.session.add(Product(**row))
        await self.session.commit()
