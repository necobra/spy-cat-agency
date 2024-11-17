from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from dependencies import get_db
from cat_spy_agency_app.crud import (
    create_mission,
    delete_mission,
    assign_cat_to_mission,
    list_missions,
    get_mission_by_id,
    partial_update_target,
    mark_target_completed,
)
from cat_spy_agency_app.schemas import (
    Mission,
    MissionCreate,
    Target,
    TargetUpdate,
)

router = APIRouter(
    prefix="/missions",
    tags=["Missions"],
)


@router.post("/", response_model=Mission, status_code=201)
async def create_new_mission(
    mission_data: MissionCreate, db: AsyncSession = Depends(get_db)
):
    return await create_mission(db, mission_data)


@router.get("/", response_model=List[Mission])
async def list_all_missions(db: AsyncSession = Depends(get_db)):
    return await list_missions(db)


@router.get("/{mission_id}", response_model=Mission)
async def get_mission(mission_id: int, db: AsyncSession = Depends(get_db)):
    mission = await get_mission_by_id(db, mission_id)
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")
    return mission


@router.patch("/targets/{target_id}", response_model=Target)
async def update_target(
    target_id: int,
    update_data: TargetUpdate,
    db: AsyncSession = Depends(get_db),
):
    return await partial_update_target(db, target_id, update_data)


@router.post("/mark_target_complete/{target_id}", response_model=Target)
async def mark_target_complete(
    target_id: int,
    db: AsyncSession = Depends(get_db),
):
    return await mark_target_completed(db, target_id)


@router.put("/{mission_id}/assign", response_model=Mission)
async def assign_cat(
    mission_id: int,
    cat_id: int,
    db: AsyncSession = Depends(get_db),
):
    return await assign_cat_to_mission(db, mission_id, cat_id)


@router.delete("/{mission_id}", status_code=204)
async def delete_existing_mission(
    mission_id: int, db: AsyncSession = Depends(get_db)
):
    await delete_mission(db, mission_id)
