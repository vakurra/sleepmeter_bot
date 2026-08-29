from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Ad


class AdService:
    """Сервис для работы с рекламными кампаниями."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, ad_id: int) -> Ad | None:
        """Возвращает рекламную кампанию по ID."""

        return await self.session.scalar(
            select(Ad).where(
                Ad.id == ad_id,
            )
        )

    async def get_by_campaign_name(
        self,
        campaign_name: str,
    ) -> Ad | None:
        """Возвращает рекламную кампанию по названию."""

        return await self.session.scalar(
            select(Ad).where(
                Ad.campaign_name == campaign_name,
            )
        )

    async def get_all(self) -> list[Ad]:
        """Возвращает все рекламные кампании."""

        stmt = select(Ad).order_by(Ad.created_at.desc())
        result = await self.session.scalars(stmt)

        return list(result.all())

    async def create(
        self,
        campaign_name: str,
        description: str,
    ) -> Ad:
        """Создает рекламную кампанию."""

        ad = Ad(
            campaign_name=campaign_name,
            description=description,
        )

        self.session.add(ad)
        await self.session.commit()

        return ad

    async def delete(
        self,
        ad: Ad,
    ) -> None:
        """Удаляет рекламную кампанию."""

        await self.session.delete(ad)
        await self.session.commit()