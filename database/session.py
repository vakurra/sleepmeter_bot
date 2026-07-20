from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from config import DB_HOST, DB_NAME, DB_PASSWORD, DB_PORT, DB_USER


# Строка подключения к MySQL через асинхронный драйвер aiomysql.
DATABASE_URL = (f"mysql+aiomysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}")

# Асинхронный движок SQLAlchemy.
engine = create_async_engine(
    DATABASE_URL,
    echo=True,  # перед деплоем поменять на false. выводит в консоль каждый запрос
)

# Фабрика для создания независимых асинхронных сессий.
SessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)