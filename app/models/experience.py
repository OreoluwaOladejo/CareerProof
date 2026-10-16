from datetime import date, datetime
from app.utils.clock import utc_now
from sqlalchemy import CheckConstraint, Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base




# One row = one job, internship, or volunteer role in a user's history.
class Experience(Base):

    __tablename__ = "experiences"

    __table_args__ = (
        # The database rejects a role that ends before it starts.
        CheckConstraint(
            "end_date IS NULL OR end_date >= start_date",
            name="ck_experiences_dates",
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

    job_title: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    company: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    location: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True,
    )

    # Date = year-month-day only (no time of day).
    start_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    # NULL  means "I still work here"
    end_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
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
        back_populates="experiences",
    )