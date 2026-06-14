# Intelligent Telegram Bot for Selling Sunglasses

Coursework MVP: Aiogram 3 Telegram bot with PostgreSQL, SQLAlchemy 2, Alembic, spaCy-based rule NLP, product import, synthetic datasets, catalog search, FAQ, and order creation.

## Requirements

- Python 3.13 installed and available through `py -3.13`
- PostgreSQL database
- Telegram bot token from BotFather

The current project targets Python 3.13 because spaCy and the coursework spec require it. Python 3.14 is not the supported runtime for this project.

## Setup

```powershell
py -3.13 -m venv .venv
.venv\Scripts\python -m pip install --upgrade pip
.venv\Scripts\python -m pip install -e .[dev]
Copy-Item .env.example .env
```

Edit `.env` and set `BOT_TOKEN` and `DATABASE_URL`.

## Database

Create the database in PostgreSQL, then run migrations:

```powershell
.venv\Scripts\python -m alembic upgrade head
```

## Datasets

Normalize and import the Amazon CSV:

```powershell
.venv\Scripts\python -m app.datasets.import_products
```

Generate synthetic product, intent, and NER datasets:

```powershell
.venv\Scripts\python -m app.datasets.generate_synthetic
```

## Run Bot

```powershell
.venv\Scripts\python -m app.main
```

## Tests

```powershell
.venv\Scripts\python -m pytest
```

## Docker

Docker is the preferred deployment path. Put `.env` in the project root with at least `BOT_TOKEN` set, then run:

```powershell
docker compose up --build
```

The bot container runs migrations, imports `app/datasets/products.csv` into PostgreSQL if the table is empty, then starts Telegram polling.
