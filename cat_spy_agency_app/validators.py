from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException
from sqlalchemy.orm import selectinload

from cat_spy_agency_app.models import SpyCat, Mission, CompleteState
from cat_spy_agency_app.schemas import Target


async def validate_spy_cat(db: AsyncSession, cat_id: int) -> SpyCat:
    result = await db.execute(
        select(SpyCat)
        .where(SpyCat.id == cat_id)
        .options(selectinload(SpyCat.missions))
    )
    cat = result.scalars().first()

    if not cat:
        raise HTTPException(status_code=404, detail="Spy Cat not found")

    if any(m.complete_state == "in_progress" for m in cat.missions):
        raise HTTPException(
            status_code=400,
            detail="Spy Cat already has an active mission",
        )

    return cat


def validate_target_count(targets: list[Target]) -> None:
    if len(targets) < 1 or len(targets) > 3:
        raise HTTPException(
            status_code=400,
            detail="A mission must have between 1 and 3 targets",
        )
