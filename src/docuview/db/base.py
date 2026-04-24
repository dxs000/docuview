from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Базовый класс для всех ORM-моделей."""

    pass


# Импортируй сюда все модели, чтобы Alembic их видел при autogenerate.
# Пока моделей нет — блок пустой, добавим потом
# from docuview.db.models import user, document  # noqa: F401
