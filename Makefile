.PHONY: help install test lint format migrate migration run clean precommit

help:
	@echo "Команды:"
	@echo "  make install     - установить зависимости + pre-commit хуки"
	@echo "  make test        - запустить тесты"
	@echo "  make lint        - проверить код (ruff + mypy)"
	@echo "  make format      - отформатировать код (black + ruff --fix)"
	@echo "  make migrate     - применить миграции Alembic"
	@echo "  make migration m=\"msg\" - создать новую миграцию"
	@echo "  make run         - запустить API (uvicorn)"
	@echo "  make precommit   - прогнать pre-commit по всем файлам"
	@echo "  make clean       - очистить кэши"

install:
	uv sync --all-extras
	uv run pre-commit install

test:
	uv run pytest -v

lint:
	uv run ruff check src tests
	uv run black --check src tests
	uv run mypy src

format:
	uv run ruff check --fix src tests
	uv run black src tests

migrate:
	uv run alembic upgrade head

migration:
	uv run alembic revision --autogenerate -m "$(m)"

run:
	uv run uvicorn docuview.main:app --reload --host 0.0.0.0 --port 8000

precommit:
	uv run pre-commit run --all-files

clean:
	rm -rf .pytest_cache .mypy_cache .ruff_cache dist build *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} +
