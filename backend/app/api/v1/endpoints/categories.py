from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db
from app.models.category import Category
from app.utils.response import success


router = APIRouter()


@router.get("")
async def list_categories(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Category).order_by(Category.id.asc()))
    items = result.scalars().all()
    return success([{"id": c.id, "name": c.name} for c in items])
