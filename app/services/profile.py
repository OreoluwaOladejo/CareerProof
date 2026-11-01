# app/services/profile_service.py
# The service layer holds the rules. The router will only translate
# HTTP into these calls. Two operations exist for a profile:
# get it, and update it. There is no create (registration does that)
# and no delete (the profile disappears with the user via CASCADE).

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.profile import Profile
from app.models.user import User
from app.schemas.profile import ProfileUpdate


class ProfileNotFound(Exception):
    # Raised if a user somehow has no profile row. Registration creates
    # one in the same transaction as the user, so this should never
    # happen. It exists so that a data problem produces a clean 404
    # instead of a crash.
    pass


def get_profile(db: Session, current_user: User) -> Profile:
    # The profile is found through the USER ID from the token, never
    # through an id sent by the client. There is nothing in the request
    # a user could change to reach someone else's profile.
    profile = db.scalar(
        select(Profile).where(Profile.user_id == current_user.id)
    )

    if profile is None:
        raise ProfileNotFound()

    return profile


def update_profile(
    db: Session,
    current_user: User,
    data: ProfileUpdate,
) -> Profile:
    profile = get_profile(db, current_user)

    # exclude_unset=True returns ONLY the fields the client actually
    # sent. This is what makes PATCH safe:
    #   {"headline": "Dev"}  -> only headline changes
    #   {"bio": null}        -> bio is cleared to NULL
    #   {}                   -> nothing changes
    # Without it, every field the client left out would be overwritten
    # with None and their profile would be wiped.
    changes = data.model_dump(exclude_unset=True)

    # setattr(profile, "headline", "Dev") is the same as
    # profile.headline = "Dev", but lets us loop over any field name.
    # Only fields that exist in ProfileUpdate can appear here, and
    # ProfileUpdate has no id or user_id, so those can never be changed.
    for field_name, value in changes.items():
        setattr(profile, field_name, value)

    # updated_at refreshes itself because the model has onupdate=utc_now.
    db.commit()

    # Reload so the returned object has the fresh updated_at.
    db.refresh(profile)
    return profile