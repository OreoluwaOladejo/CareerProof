from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.profile import Profile
from app.models.user import User
from app.schemas.user import UserCreate
from app.utils.security import hash_password
from app.utils.security import verify_password


class EmailAlreadyRegistered(Exception):
    # Raised when someone tries to register an email that exists.
    # The router will turn this into an HTTP 409.
    pass


class InvalidCredentials(Exception):
    # Raised for ANY login failure (unknown email, wrong password,
    # inactive account). One exception for all of them, so the caller
    # cannot accidentally tell the client which one it was.
    pass


'''This line creates a fake password hash when the application starts.
   Suppose an attacker tries to log in.  
   Case A: The email doesn't exist. Your application could immediately reject the request.
   Case B: The email exists, but the password is wrong. Your application must perform a password-hash verification, which takes some time.
   If Case A consistently responds faster than Case B, an attacker might use response timing to guess which email addresses have accounts.
   My code attempts to reduce that timing difference by performing a dummy password verification for unknown emails.
'''
_DUMMY_HASH = hash_password("not-a-real-password")

'''-> User | None Genuinly just mean that that class must return 
    Either a user or nothing '''
def get_user_by_email(db: Session, email: str) -> User | None:
    # select(User).where(...) builds the query; db.scalar runs it and
    # returns the first matching User, or None if there is no match.
    return db.scalar(
        select(User).where(User.email == email)
        )


def register_user(db: Session, user_in: UserCreate) -> User:
    # Friendly early check, so the common case gives a clean error.
    if get_user_by_email(db, user_in.email) is not None:
        raise EmailAlreadyRegistered()

    user = User(
        email=user_in.email,
        # We store only the hash, never the password itself.
        password_hash=hash_password(user_in.password),
    )

    # Create the empty profile now, attached to this user. Because they
    # are added together, they are saved in ONE transaction: either both
    # rows exist, or neither does. SQLAlchemy fills in profile.user_id
    # for us from the relationship.
    user.profile = Profile()

    db.add(user)

    try:
        db.commit()
    except IntegrityError:
        # The check above is not enough on its own. If two requests with
        # the same email arrive at the same instant, both can pass the
        # check. The database's unique constraint is the real guard, and
        # this is where we catch it. rollback() cancels the failed
        # transaction so the session is usable again.
        db.rollback()
        raise EmailAlreadyRegistered()

    # Reload the user from the database so generated values (id,
    # created_at) are present on the object we return.
    db.refresh(user)
    return user


def authenticate_user(db: Session, email: str, password: str) -> User:
    # The login form does not pass through UserCreate, so the email is
    # NOT lowercased for us. We normalize it here, the same way.
    normalized_email = email.strip().lower()

    user = get_user_by_email(db, normalized_email)

    if user is None:
        # Spend the same time as a real check, then fail.
        verify_password(password, _DUMMY_HASH)
        raise InvalidCredentials()

    if not verify_password(password, user.password_hash):
        raise InvalidCredentials()

    if not user.is_active:
        raise InvalidCredentials()

    return user