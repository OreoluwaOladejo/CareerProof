from datetime import date, datetime
from app.utils.clock import utc_now

from sqlalchemy import CheckConstraint, Date, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base




# One row = one school, degree, or programme.
class Education(Base):

    __tablename__ = "educations"

    __table_args__ = (
        CheckConstraint(
            "end_date IS NULL OR end_date >= start_date",
            name="ck_educations_dates",
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

    institution: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    # e.g. "BSc"
    degree: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    # e.g. "Computer Science"
    field_of_study: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True,
    )

    start_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    # NULL = still studying 
    end_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    # Text, not a number: grading differs by country ("First Class",
    # "4.5/5.0", "3.8 GPA"), so I am just  storing whatever the user writes.
    grade: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
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

    user: Mapped["User"] = relationship(
        back_populates="educations",
    )