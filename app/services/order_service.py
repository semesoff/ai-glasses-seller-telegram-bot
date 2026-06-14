from app.database.models import Order
from app.database.repositories import OrderRepository, ProductRepository


class OrderService:
    def __init__(self, orders: OrderRepository, products: ProductRepository):
        self.orders = orders
        self.products = products

    async def create_order(self, telegram_id: int, product_id: int, phone: str, address: str) -> Order:
        product = await self.products.get_by_id(product_id)
        if product is None:
            raise ValueError(f"Product {product_id} does not exist")
        return await self.orders.create(telegram_id=telegram_id, product_id=product_id, phone=phone, address=address)

    async def get_user_orders(self, telegram_id: int, limit: int = 10) -> list[Order]:
        return await self.orders.get_by_telegram_id(telegram_id, limit=limit)
