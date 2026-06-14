import pytest

from app.services.order_service import OrderService


class ProductRepoStub:
    async def get_by_id(self, product_id: int):
        return None


class OrderRepoStub:
    async def create(self, telegram_id: int, product_id: int, phone: str, address: str):
        raise AssertionError("create should not be called for missing product")


@pytest.mark.asyncio
async def test_order_service_rejects_missing_product() -> None:
    service = OrderService(OrderRepoStub(), ProductRepoStub())

    with pytest.raises(ValueError):
        await service.create_order(telegram_id=1, product_id=999, phone="+79990000000", address="Moscow")

