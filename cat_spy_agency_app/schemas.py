from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator, ConfigDict


class CompleteState(str, Enum):
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class TargetBase(BaseModel):
    name: str = Field(..., max_length=255)
    country: str = Field(..., max_length=255)
    notes: Optional[str] = Field(None, max_length=2047)


class TargetCreate(TargetBase):
    complete_state: CompleteState = CompleteState.IN_PROGRESS
    mission_id: int


class Target(TargetBase):
    id: int
    complete_state: CompleteState
    mission_id: int

    model_config = ConfigDict(from_attributes=True)


class TargetUpdate(BaseModel):
    notes: Optional[str]

    model_config = ConfigDict(from_attributes=True)


class MissionBase(BaseModel):
    complete_state: CompleteState = CompleteState.IN_PROGRESS
    targets: List[Target] = Field(default_factory=list)
    spy_cat_id: Optional[int] = None


class MissionCreate(MissionBase):
    targets: List[TargetBase] = Field(default_factory=list)


class Mission(MissionBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


class SpyCatBase(BaseModel):
    name: str = Field(..., max_length=255)
    years_of_experience: int
    breed: str = Field(..., max_length=511)
    salary: int


class SpyCatCreate(SpyCatBase):
    @field_validator("salary")
    def validate_salary(cls, salary: int):
        if salary < 0:
            raise ValueError("Salary cannot be negative.")
        return salary


class SpyCat(SpyCatBase):
    id: int
    missions: List[Mission] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)
