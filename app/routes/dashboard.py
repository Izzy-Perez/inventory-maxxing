from fastapi import APIRouter, Depends, Request
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Asset, AssetStatus, AssetType
from app.templating import templates

router = APIRouter()


@router.get("/")
async def dashboard(request: Request, db: AsyncSession = Depends(get_db)):
    total = await db.scalar(select(func.count(Asset.id)))
    active = await db.scalar(
        select(func.count(Asset.id)).where(Asset.status == AssetStatus.ACTIVE)
    )
    disposed = await db.scalar(
        select(func.count(Asset.id)).where(Asset.status == AssetStatus.DISPOSED)
    )
    by_type = (
        await db.execute(
            select(Asset.asset_type, func.count(Asset.id))
            .group_by(Asset.asset_type)
        )
    ).all()

    return templates.TemplateResponse(
        request,
        "dashboard.html",
        {
            "total": total or 0,
            "active": active or 0,
            "disposed": disposed or 0,
            "by_type": by_type,
        },
    )
