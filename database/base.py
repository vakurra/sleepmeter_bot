from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Базовый класс для всех SQLAlchemy-моделей проекта."""

    def __repr__(self) -> str:
        attrs = ", ".join(
            f"{column.name}={getattr(self, column.name)!r}"
            for column in self.__table__.columns
        )
        return f"{self.__class__.__name__}({attrs})"