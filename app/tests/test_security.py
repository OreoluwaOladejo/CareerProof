from datetime import timedelta

import jwt

from app.config import settings
from app.utils.security import create_access_token
from app.utils.security import decode_access_token
from app.utils.security import hash_password
from app.utils.security import verify_password


def test_hash_is_not_the_plain_password():
    hashed = hash_password("correct horse battery")
    assert hashed != "correct horse battery"


def test_correct_password_verifies():
    hashed = hash_password("correct horse battery")
    assert verify_password("correct horse battery", hashed) is True


def test_wrong_password_is_rejected():
    hashed = hash_password("correct horse battery")
    assert verify_password("wrong password", hashed) is False


def test_same_password_gives_different_hashes():
    # Proves the random salt is working.
    assert hash_password("same") != hash_password("same")


def test_garbage_hash_is_rejected_not_crashed():
    assert verify_password("anything", "not-a-real-hash") is False


def test_token_round_trip_returns_user_id():
    token = create_access_token(42)
    assert decode_access_token(token) == 42


def test_expired_token_is_rejected():
    token = create_access_token(42, expires_delta=timedelta(seconds=-1))
    assert decode_access_token(token) is None


def test_tampered_token_is_rejected():
    token = create_access_token(42)
    tampered = token[:-1] + ("A" if token[-1] != "A" else "B")
    assert decode_access_token(tampered) is None


def test_token_signed_with_wrong_key_is_rejected():
    forged = jwt.encode(
        {"sub": "42", "exp": 9999999999},
        "some-other-secret",
        algorithm=settings.algorithm,
    )
    assert decode_access_token(forged) is None


def test_garbage_token_is_rejected():
    assert decode_access_token("not.a.token") is None