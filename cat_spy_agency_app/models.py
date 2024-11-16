from typing import Any
from sqlalchemy import String, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.declarative import declarative_base
from enum import Enum as PyEnum

Base = declarative_base()


class CompleteState(PyEnum):
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class SpyCat(Base):
    __tablename__ = "spy_cat"

    id: Mapped[int] = mapped_column(primary_key=True, nullable=False)

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    years_of_experience: Mapped[int] = mapped_column(nullable=False)
    breed: Mapped[str] = mapped_column(String(511), nullable=False)
    salary: Mapped[int] = mapped_column(nullable=False)

    missions: Mapped[list["Mission"]] = relationship(
        "Mission", back_populates="spy_cat", collection_class=list
    )


class Mission(Base):
    __tablename__ = "mission"

    id: Mapped[int] = mapped_column(primary_key=True, nullable=False)

    complete_state: Mapped[CompleteState] = mapped_column(
        Enum(CompleteState), nullable=False, default=CompleteState.IN_PROGRESS
    )

    spy_cat_id: Mapped[int] = mapped_column(
        ForeignKey("spy_cat.id"), nullable=True
    )
    spy_cat: Mapped[SpyCat] = relationship("SpyCat", back_populates="missions")

    targets: Mapped[list["Target"]] = relationship(
        "Target", back_populates="mission", collection_class=list
    )


class Target(Base):
    __tablename__ = "target"

    id: Mapped[int] = mapped_column(primary_key=True, nullable=False)

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    country: Mapped[str] = mapped_column(String(255), nullable=False)
    notes: Mapped[str] = mapped_column(String(2047))

    complete_state: Mapped[CompleteState] = mapped_column(
        Enum(CompleteState), nullable=False, default=CompleteState.IN_PROGRESS
    )

    mission_id: Mapped[int] = mapped_column(
        ForeignKey("mission.id"), nullable=False
    )
    mission: Mapped["Mission"] = relationship(
        "Mission", back_populates="targets"
    )
