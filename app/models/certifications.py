from datetime import date, datetime
from app.utils.clock import utc_now

from sqlalchemy import CheckConstraint, Date, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base




# One row = one certificate (e.g. "AWS Cloud Practitioner").
class Certification(Base):

    __tablename__ = "certifications"

    __table_args__ = (
      
        # NULL expiry_date = "does not expire".
        CheckConstraint(
            "expiry_date IS NULL OR expiry_date >= issue_date",
            name="ck_certifications_dates",
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

    name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    issuing_organization: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    issue_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    expiry_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    # The ID printed on the certificate, and a link where anyone can verify it.
    credential_id: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    credential_url: Mapped[str | None] = mapped_column(
        String(500),
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
        back_populates="certifications",
    )