from datetime import datetime
from datetime import timedelta

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError
from argon2.exceptions import VerifyMismatchError

from app.config import settings
from app.utils.clock import utc_now

_hasher = PasswordHasher()
def hash_password(password: str) -> str:
    return _hasher.hash(password)
def verify_password(plain_password: str, password_hash: str) -> bool:
    try:
        # To check a login we hash the typed password again and compare it
        # with the stored hash. Argon2 does that comparison for us.
        return _hasher.verify(password_hash, plain_password)
    except (VerifyMismatchError, InvalidHashError):
        # Wrong password, or a stored hash that is not a valid Argon2
        # hash. Either way the answer is simply "no". We return False
        # instead of raising, so callers never leak WHY it failed.
        return False
def create_access_token(user_id: int, expires_delta: timedelta | None = None) -> str:
    # A JWT is three parts joined by dots: header.payload.signature.
    # The payload is only ENCODED, not encrypted, so anyone can read it.
    # NEVER put secrets in it. The signature is what protects it: it
    # proves the token was issued by us and has not been edited.
    if expires_delta is None:
        expires_delta = timedelta(minutes=settings.access_token_expire_minutes)
        #So like your expire_delta is always going to None
        #So you are the one that is now going to import the token time 
        #from your setting object in your config 
    issued_at = utc_now()
    payload = {
        # "sub" (subject) = who this token belongs to. PyJWT requires
        # it to be a string, so we convert the integer id.
        "sub": str(user_id),
        # "iat" = issued at. "exp" = expires at. After "exp", decoding
        # fails automatically, which is how tokens stop working.
        "iat": issued_at,
        "exp": issued_at + expires_delta,
    }
    #This uses PyJWT to create the encoded token.
    #payload supplies the claims(Which is sub,iat and exp)
    #settings.secret_key supplies the secret used to sign the token.
    #algorithm=settings.algorithm specifies the signing algorithm, such as HS256.
    #Remember header.payload.signature
    return jwt.encode(
        payload,
        settings.secret_key,
        algorithm=settings.algorithm,
    )

#Creating a token is only half the job. 
# When the user makes a request to a protected endpoint,
#  your application must check that the token is valid.
def decode_access_token(token: str) -> int | None:
    # Returns the user id if the token is genuine and still valid,
    # otherwise None. Callers treat None as "not logged in".
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            # Always pass the allowed algorithms explicitly. Never let
            # the token itself decide how it should be verified.
            algorithms=[settings.algorithm],
            # Reject tokens that are missing these claims.
            options={"require": ["exp", "sub"]},
        )
        return int(payload["sub"])
    except (jwt.PyJWTError, ValueError):
        # PyJWTError covers: expired, bad signature, malformed token.
        # ValueError covers a "sub" that is not a number.
        return None




