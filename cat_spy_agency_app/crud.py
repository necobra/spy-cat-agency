from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload, selectinload
from fastapi import HTTPException

from cat_spy_agency_app.validators import (
    validate_target_count,
    validate_spy_cat,
)
from cat_spy_agency_app.models import (
    SpyCat,
    Mission,
    Target,
)
from cat_spy_agency_app import schemas


async def create_spy_cat(
    db: AsyncSession,
    cat: schemas.SpyCatCreate,
) -> schemas.SpyCat:
    new_cat = SpyCat(**cat.model_dump())
    db.add(new_cat)

    await db.commit()
    await db.refresh(new_cat)

    result = await db.execute(
        select(SpyCat)
        .options(selectinload(SpyCat.missions))
        .where(SpyCat.id == new_cat.id)
    )
    new_cat_with_relationships = result.scalars().first()

    return new_cat_with_relationships


async def remove_spy_cat(db: AsyncSession, cat_id: int) -> None:
    result = await db.execute(select(SpyCat).where(SpyCat.id == cat_id))
    cat = result.scalars().first()
    if not cat:
        raise HTTPException(status_code=404, detail="Spy Cat not found")
    await db.delete(cat)
    await db.commit()


async def update_spy_cat_salary(
    db: AsyncSession,
    cat_id: int,
    salary: int,
) -> schemas.SpyCat:
    if salary < 0:
        raise HTTPException(
            status_code=400, detail="Salary cannot be negative"
        )
    cat = await get_spy_cat(db, cat_id)
    await db.commit()
    await db.refresh(cat)
    return cat


async def list_spy_cats(db: AsyncSession) -> list[schemas.SpyCat]:
    result = await db.execute(
        select(SpyCat).options(selectinload(SpyCat.missions))
    )
    cats = result.scalars().all()
    return list(cats)


async def get_spy_cat(db: AsyncSession, cat_id: int) -> schemas.SpyCat:
    result = await db.execute(
        select(SpyCat)
        .where(SpyCat.id == cat_id)
        .options(selectinload(SpyCat.missions))
    )
    cat = result.scalars().first()
    if not cat:
        raise HTTPException(status_code=404, detail="Spy Cat not found")
    return cat


async def create_mission(
    db: AsyncSession, mission_data: schemas.MissionCreate
) -> Mission:
    validate_target_count(mission_data.targets)

    if mission_data.spy_cat_id is not None:
        await validate_spy_cat(db, mission_data.spy_cat_id)

    new_mission = Mission(spy_cat_id=mission_data.spy_cat_id)
    db.add(new_mission)
    await db.flush()

    for target_data in mission_data.targets:
        new_target = Target(
            name=target_data.name,
            country=target_data.country,
            notes=target_data.notes,
            mission_id=new_mission.id,
        )
        db.add(new_target)

    await db.commit()

    result = await db.execute(
        select(Mission)
        .where(Mission.id == new_mission.id)
        .options(
            selectinload(Mission.targets),
            selectinload(Mission.spy_cat),
        )
    )
    new_mission_with_relationships = result.scalars().first()

    return new_mission_with_relationships


async def delete_mission(db: AsyncSession, mission_id: int) -> None:
    mission = await get_mission(db, mission_id)
    if mission.spy_cat:
        raise HTTPException(
            status_code=400,
            detail="Mission is assigned to a cat and cannot be deleted",
        )
    await db.delete(mission)
    await db.commit()


async def update_mission_targets(
    db: AsyncSession, mission_id: int, update_data: schemas.MissionUpdate
) -> Mission:
    mission = await get_mission(db, mission_id)

    for target_data in update_data.targets:
        result = await db.execute(
            select(Target).where(Target.id == target_data.id)
        )
        target = result.scalars().first()
        if not target:
            raise HTTPException(
                status_code=404,
                detail=f"Target with ID {target_data.id} not found",
            )
        if target.complete_state == "completed":
            raise HTTPException(
                status_code=400,
                detail=f"Cannot update completed target with ID {target.id}",
            )
        target.notes = target_data.notes
        db.add(target)

    await db.commit()
    await db.refresh(mission)
    return mission


async def mark_target_complete(db: AsyncSession, target_id: int) -> Target:
    result = await db.execute(
        select(Target)
        .where(Target.id == target_id)
        .options(joinedload(Target.mission))
    )
    target = result.scalars().first()
    if not target:
        raise HTTPException(status_code=404, detail="Target not found")
    if target.complete_state == "completed":
        raise HTTPException(
            status_code=400,
            detail="Target is already marked as completed",
        )

    target.complete_state = "completed"
    await db.commit()

    mission = target.mission
    all_targets = await db.execute(
        select(Target).where(Target.mission_id == mission.id)
    )
    if all(
        t.complete_state == "completed" for t in all_targets.scalars().all()
    ):
        mission.complete_state = "completed"
        await db.commit()

    await db.refresh(target)
    return target


async def list_missions(db: AsyncSession) -> list[schemas.Mission]:
    result = await db.execute(
        select(Mission).options(
            selectinload(Mission.targets),
            selectinload(Mission.spy_cat),
        )
    )
    missions = result.scalars().all()
    return list(missions)


async def get_mission(db: AsyncSession, mission_id: int) -> Mission:
    result = await db.execute(
        select(Mission)
        .where(Mission.id == mission_id)
        .options(
            joinedload(Mission.spy_cat),
            joinedload(Mission.targets),
        )
    )
    mission = result.scalars().first()
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")
    return mission


async def assign_cat_to_mission(
    db: AsyncSession, mission_id: int, cat_id: int
) -> Mission:
    mission = await get_mission(db, mission_id)
    if mission.spy_cat:
        raise HTTPException(
            status_code=400, detail="Mission is already assigned to a cat"
        )

    await validate_spy_cat(db, cat_id)

    mission.spy_cat_id = cat_id
    await db.commit()
    await db.refresh(mission)
    return mission
