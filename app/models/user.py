from datetime import datetime
from typing import Optional
from app.utils.clock import utc_now
from sqlalchemy import Boolean, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class User(Base):

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    email: Mapped[str] = mapped_column(
        String,
        unique=True,
        nullable=False,
    )

    password_hash: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    )

    profile: Mapped[Optional["Profile"]] = relationship(
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )
    skills: Mapped[list["Skill"]] = relationship(
    back_populates="user",
    cascade="all, delete-orphan",)
        # Same pattern as skills: a list per user, and deleting the user
    # deletes all of these rows too (needed for the delete-account endpoint).
    experiences: Mapped[list["Experience"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )

    projects: Mapped[list["Project"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )

    educations: Mapped[list["Education"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )

    certifications: Mapped[list["Certification"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
