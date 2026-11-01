
from datetime import datetime
from typing import Literal

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field
from pydantic import field_validator

# The only allowed proficiency values. This mirrors the CHECK constraint
# in the model, so bad values are rejected with a 422 here instead of a
# database error later.
Proficiency = Literal["beginner", "intermediate", "advanced"]


def _clean_name(value: str) -> str:
    # Trim spaces, then reject anything that is blank. "   " has three
    # characters, so it would pass min_length=1 without this check.
    cleaned = value.strip()
    if not cleaned:
        raise ValueError("name must not be blank")
    return cleaned


def _clean_category(value: str | None) -> str | None:
    # category is optional. None or blank both mean "no category", and
    # both are stored as NULL, never as an empty string.
    if value is None:
        return None
    cleaned = value.strip()
    if not cleaned:
        return None
    return cleaned


def _lowercase_proficiency(value):
    # mode="before" validators run BEFORE the Literal check, so
    # "Advanced" becomes "advanced" first. Non-strings are passed on
    # unchanged and rejected by the Literal check afterwards.
    if isinstance(value, str):
        return value.strip().lower()
    return value


class SkillCreate(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=100,
    )
    category: str | None = Field(
        default=None,
        max_length=50,
    )
    # Defaults to beginner, the same default the model uses.
    proficiency: Proficiency = "beginner"

    @field_validator("name")
    @classmethod
    def clean_name(cls, value: str) -> str:
        return _clean_name(value)

    @field_validator("category")
    @classmethod
    def clean_category(cls, value: str | None) -> str | None:
        return _clean_category(value)

    @field_validator("proficiency", mode="before")
    @classmethod
    def lowercase_proficiency(cls, value):
        return _lowercase_proficiency(value)


class SkillUpdate(BaseModel):
    # Every field is optional, so PATCH can change just one thing.
    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )
    category: str | None = Field(
        default=None,
        max_length=50,
    )
    proficiency: Proficiency | None = None

    @field_validator("name")
    @classmethod
    def clean_name(cls, value: str | None) -> str:
        # These validators only run when the client actually SENT the
        # field. Sending "name": null would try to write NULL into a
        # NOT NULL column, so we reject it here with a clean 422.
        if value is None:
            raise ValueError("name cannot be null")
        return _clean_name(value)

    @field_validator("category")
    @classmethod
    def clean_category(cls, value: str | None) -> str | None:
        # Unlike name, sending null is allowed: it clears the category.
        return _clean_category(value)

    @field_validator("proficiency", mode="before")
    @classmethod
    def lowercase_proficiency(cls, value):
        # proficiency is NOT NULL in the database, so null is rejected.
        if value is None:
            raise ValueError("proficiency cannot be null")
        return _lowercase_proficiency(value)


class SkillResponse(BaseModel):
    # Lets Pydantic read values straight off a SQLAlchemy Skill object.
    model_config = ConfigDict(from_attributes=True)

    # Unlike Profile, skills DO return an id, because the client needs
    # it for /skills/{skill_id}. user_id is still never returned.
    id: int
    name: str
    category: str | None
    proficiency: str
    created_at: datetime
    updated_at: datetime