from datetime import datetime
from app.utils.clock import utc_now
from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


# One row = ONE skill belonging to ONE user.
class Skill(Base):

    __tablename__ = "skills"

    # __table_args__ holds rules that involve the whole table, not one column.
    __table_args__ = (
        # A user can't list the same skill name twice (e.g. "Python" twice).
        UniqueConstraint("user_id", "name", name="uq_skills_user_id_name"),
        CheckConstraint(
            "proficiency IN ('beginner', 'intermediate', 'advanced')",
            name="ck_skills_proficiency",
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # The skill's name, e.g. "Python", "Docker", "Communication".
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    # Optional grouping, e.g. "language", "framework", "tool", "soft skill".
  
    category: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    proficiency: Mapped[str] = mapped_column(
        String(20),
        default="beginner",
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

    # Gives us skill.user -> the User who owns this skill.
    user: Mapped["User"] = relationship(
        back_populates="skills",
    )