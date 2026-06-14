import asyncio

from app.config import get_settings
from app.database.repositories import ProductRepository
from app.database.session import SessionFactory
from app.datasets.normalization import read_products, write_products_csv


async def main() -> None:
    settings = get_settings()
    source = settings.source_products_csv if settings.source_products_csv.exists() else settings.normalized_products_csv
    rows = read_products(source)
    write_products_csv(settings.normalized_products_csv, rows)
    async with SessionFactory() as session:
        repository = ProductRepository(session)
        if await repository.count():
            print("Products table is not empty, skipping import")
            return
        await repository.bulk_insert(rows)
    print(f"Imported {len(rows)} products from {source}")


if __name__ == "__main__":
    asyncio.run(main())
