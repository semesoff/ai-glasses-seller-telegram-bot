from app.database.models import Product
from app.database.repositories import ProductRepository
from app.services.nlp_service import NLPService


class ProductService:
    page_size = 5

    def __init__(self, repository: ProductRepository, nlp: NLPService | None = None):
        self.repository = repository
        self.nlp = nlp or NLPService()

    async def get_catalog(self, page: int = 1) -> list[Product]:
        page = max(page, 1)
        return await self.repository.get_all(limit=self.page_size, offset=(page - 1) * self.page_size)

    async def get_product(self, product_id: int) -> Product | None:
        return await self.repository.get_by_id(product_id)

    async def search_products(self, query: str, page: int = 1) -> list[Product]:
        result = self.nlp.analyze(query)
        page = max(page, 1)
        return await self.repository.find_by_filters(result.entities, limit=self.page_size, offset=(page - 1) * self.page_size)

    async def find_by_filters(self, filters: dict, page: int = 1, limit: int | None = None) -> list[Product]:
        page = max(page, 1)
        page_size = limit or self.page_size
        query_filters = {key: value for key, value in filters.items() if key != "page"}
        return await self.repository.find_by_filters(query_filters, limit=page_size, offset=(page - 1) * page_size)
