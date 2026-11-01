# app/schemas/profile.py
# There is NO ProfileCreate. A profile is created empty at registration
# (see register_user), so the client never creates one. They only
# VIEW it (ProfileResponse) and EDIT it (ProfileUpdate).

from datetime import datetime
from urllib.parse import urlparse

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field
from pydantic import field_validator


def _clean_text(value: str | None) -> str | None:
    # Shared helper so every text field is cleaned the same way.
    # None means "no value", so we pass it through untouched.
    if value is None:
        return None
    cleaned = value.strip()
    # An empty or all-space string becomes None. That way "clear this
    # field" is stored as NULL, never as a meaningless "".
    if not cleaned:
        return None
    else:
        return cleaned


def _clean_url(value: str | None) -> str | None:
    cleaned = _clean_text(value)
    if cleaned is None:
        return None
    parsed = urlparse(cleaned)
    # Only http and https are allowed. This blocks values like
    # "javascript:alert(1)", which would be dangerous once a frontend
    # renders this value as a clickable link.
    # netloc is the domain part; "https://" alone has none.
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        raise ValueError("must be a full URL starting with http:// or https://")
    return cleaned


class ProfileUpdate(BaseModel):
    first_name: str | None = Field(default=None, max_length=100)
    last_name: str | None = Field(default=None, max_length=100)
    headline: str | None = Field(default=None, max_length=255)
    # bio is a Text column (no database limit), so we set our own limit.
    bio: str | None = Field(default=None, max_length=2000)
    location: str | None = Field(default=None, max_length=150)
    linkedin_url: str | None = Field(default=None, max_length=500)
    github_url: str | None = Field(default=None, max_length=500)
    portfolio_url: str | None = Field(default=None, max_length=500)

    @field_validator(
        "first_name",
        "last_name",
        "headline",
        "bio",
        "location",
    )
    @classmethod
    def clean_text_fields(cls, value: str | None) -> str | None:
        return _clean_text(value)

    @field_validator(
        "linkedin_url",
        "github_url",
        "portfolio_url",
    )
    @classmethod
    def clean_url_fields(cls, value: str | None) -> str | None:
        return _clean_url(value)


class ProfileResponse(BaseModel):
    # Lets Pydantic read values straight off a SQLAlchemy Profile object.
    model_config = ConfigDict(from_attributes=True)

    # Deliberately no id or user_id: the client reaches the profile
    # through its token, so it never needs either of them.
    first_name: str | None
    last_name: str | None
    headline: str | None
    bio: str | None
    location: str | None
    linkedin_url: str | None
    github_url: str | None
    portfolio_url: str | None
    created_at: datetime
    updated_at: datetime