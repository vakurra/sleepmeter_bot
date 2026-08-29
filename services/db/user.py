from datetime import date, datetime, time, timedelta, timezone

from aiogram.types import User as TgUser
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import User, UserRole


class UserService:
    """Сервис для работы с пользователями."""

    def __init__(self, session: AsyncSession):
        self.session = session


    async def get_by_id(self, user_id: int) -> User | None:
        """Возвращает пользователя по Telegram ID."""

        return await self.session.scalar(select(User).where(User.id == user_id))


    async def get_all(self) -> list[User]:
        """Возвращает всех пользователей."""

        stmt = select(User).order_by(User.created_at.desc())
        result = await self.session.scalars(stmt)

        return list(result.all())


    async def get_new(self, days: int) -> list[User]:
        """Возвращает пользователей, зарегистрированных за последние N дней."""

        since = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=days)

        stmt = (
            select(User)
            .where(User.created_at >= since)
            .order_by(User.created_at.desc())
        )

        result = await self.session.scalars(stmt)

        return list(result.all())

    
    async def get_admins(self) -> list[User]:
        """Возвращает всех администраторов."""

        stmt = select(User).where(User.role == UserRole.ADMIN)
        result = await self.session.scalars(stmt)

        return list(result.all())
    

    async def create(
        self,
        tg_user: TgUser,
        utc_offset: int,
        reminder_time: time,
        referred_by: str | None = None,
    ) -> User:
        """Создает нового пользователя."""

        local_datetime = datetime.now(timezone.utc) + timedelta(hours=utc_offset)

        last_reminder_date = (
            local_datetime.date()
            if local_datetime.time().replace(tzinfo=None) >= reminder_time
            else None
        )

        user = User(
            id=tg_user.id,
            username=tg_user.username,
            first_name=tg_user.first_name,
            utc_offset=utc_offset,
            reminder_time=reminder_time,
            referred_by=referred_by,
            last_reminder_date=last_reminder_date,
        )

        self.session.add(user)
        await self.session.commit()
        return user


    async def get_reminder_candidates(self) -> list[User]:
        """Возвращает пользователей, которым могут быть отправлены уведомления."""

        stmt = select(User).where(User.notifications_enabled)

        result = await self.session.scalars(stmt)

        return list(result.all())


    def update_last_reminder_date(
        self,
        user: User,
        reminder_date: date,
    ) -> None:
        """Обновляет дату последнего обработанного напоминания."""

        user.last_reminder_date = reminder_date


    def update_utc_offset(
        self,
        user: User,
        utc_offset: int,
    ) -> None:
        """Изменяет смещение часового пояса пользователя относительно UTC."""

        user.utc_offset = utc_offset


    def update_reminder_time(
        self,
        user: User,
        reminder_time: time,
    ) -> None:
        """Изменяет локальное время ежедневного напоминания."""

        user.reminder_time = reminder_time


    def update_notifications_enabled(
        self,
        user: User,
        enabled: bool,
    ) -> None:
        """Включает или отключает ежедневные уведомления."""

        user.notifications_enabled = enabled
