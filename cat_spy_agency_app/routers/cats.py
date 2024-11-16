from aiocache import cached
import httpx
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from dependencies import get_db
from cat_spy_agency_app.schemas import SpyCat, SpyCatCreate
from cat_spy_agency_app.crud import (
    create_spy_cat,
    remove_spy_cat,
    update_spy_cat_salary,
    list_spy_cats,
    get_spy_cat,
)

router = APIRouter(
    prefix="/spy_cats",
    tags=["Spy Cats"],
)


@cached(ttl=3600)
async def fetch_breeds():
    async with httpx.AsyncClient(timeout=300) as client:
        try:
            response = await client.get("https://api.thecatapi.com/v1/breeds")
            response.raise_for_status()
            return [b["name"] for b in response.json()]
        except httpx.RequestError as e:
            raise HTTPException(
                status_code=500,
                detail="Failed to fetch breeds from TheCatAPI due to network error.",
            )
        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to fetch breeds: HTTP {e.response.status_code}.",
            )


async def validate_breed(breed: str):
    try:
        breeds = await fetch_breeds()
        if breed not in breeds:
            raise HTTPException(
                status_code=400,
                detail=f"Breed '{breed}' is not valid. Available breeds: {', '.join(breeds)}",
            )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"An unexpected error occurred: {str(e)}"
        )


@router.post("/", response_model=SpyCat, status_code=201)
async def create_cat(
    cat_data: SpyCatCreate, db: AsyncSession = Depends(get_db)
):
    await validate_breed(cat_data.breed)
    result = await create_spy_cat(db, cat_data)
    return result


@router.delete("/{cat_id}", status_code=204)
async def delete_cat(cat_id: int, db: AsyncSession = Depends(get_db)):
    await remove_spy_cat(db, cat_id)
    return {"message": "Spy Cat deleted successfully"}


@router.put("/{cat_id}/salary", response_model=SpyCat)
async def update_cat_salary(
    cat_id: int, salary: int, db: AsyncSession = Depends(get_db)
):
    return await update_spy_cat_salary(db, cat_id, salary)


@router.get("/", response_model=List[SpyCat])
async def get_all_cats(db: AsyncSession = Depends(get_db)):
    return await list_spy_cats(db)


@router.get("/{cat_id}", response_model=SpyCat)
async def get_cat(cat_id: int, db: AsyncSession = Depends(get_db)):
    return await get_spy_cat(db, cat_id)
