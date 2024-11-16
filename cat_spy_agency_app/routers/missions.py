from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from dependencies import get_db
from cat_spy_agency_app.crud import (
    create_mission,
    delete_mission,
    update_mission_targets,
    assign_cat_to_mission,
    list_missions,
    get_mission,
)
from cat_spy_agency_app.schemas import (
    Mission,
    MissionCreate,
    MissionUpdate,
)

router = APIRouter(
    prefix="/missions",
    tags=["Missions"],
)


@router.post("/", response_model=Mission, status_code=201)
async def create_new_mission(
    mission_data: MissionCreate, db: AsyncSession = Depends(get_db)
):
    try:
        return await create_mission(db, mission_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=List[Mission])
async def list_all_missions(db: AsyncSession = Depends(get_db)):
    return await list_missions(db)


@router.get("/{mission_id}", response_model=Mission)
async def get_mission(mission_id: int, db: AsyncSession = Depends(get_db)):
    mission = await get_mission(db, mission_id)
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")
    return mission


@router.put("/{mission_id}/targets", response_model=Mission)
async def update_targets(
    mission_id: int,
    update_data: MissionUpdate,
    db: AsyncSession = Depends(get_db),
):
    try:
        return await update_mission_targets(db, mission_id, update_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{mission_id}/assign", response_model=Mission)
async def assign_cat(
    mission_id: int,
    cat_id: int,
    db: AsyncSession = Depends(get_db),
):
    try:
        return await assign_cat_to_mission(db, mission_id, cat_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{mission_id}", status_code=204)
async def delete_existing_mission(
    mission_id: int, db: AsyncSession = Depends(get_db)
):
    try:
        await delete_mission(db, mission_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
