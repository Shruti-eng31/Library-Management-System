import base64
import hashlib
import hmac
import os
from typing import Dict, Tuple

# These defaults keep password hashing consistent across the app.
_PBKDF2_ALGORITHM = "sha256"
_PBKDF2_ITERATIONS = 260_000
_SALT_BYTES = 16


def _decode_salt(salt: str) -> bytes:
    return base64.b64decode(salt.encode("utf-8"))


def _encode_bytes(raw: bytes) -> str:
    return base64.b64encode(raw).decode("utf-8")


def generate_salt() -> str:
    """Generate a cryptographically secure salt encoded as base64."""
    return _encode_bytes(os.urandom(_SALT_BYTES))


def hash_password(password: str, salt: str | None = None) -> Tuple[str, str]:
    """Create a PBKDF2 hash for the provided password.

    Returns a tuple of (password_hash, salt) where both values are base64 strings.
    """
    if salt is None:
        salt = generate_salt()

    password_hash = hashlib.pbkdf2_hmac(
        _PBKDF2_ALGORITHM,
        password.encode("utf-8"),
        _decode_salt(salt),
        _PBKDF2_ITERATIONS,
    )

    return _encode_bytes(password_hash), salt


def verify_password(password: str, password_hash: str | None, salt: str | None) -> bool:
    """Verify a plaintext password against a stored hash and salt."""
    if not password_hash or not salt:
        return False

    candidate_hash, _ = hash_password(password, salt)
    return hmac.compare_digest(candidate_hash, password_hash)


def ensure_password_fields(user: Dict[str, str]) -> bool:
    """Ensure the given user dict stores hashed credentials only.

    If a legacy ``password`` field is present it will be converted to
    ``password_hash`` + ``password_salt``. Returns True when a mutation occurs.
    """
    mutated = False

    if "password_hash" in user and "password_salt" in user:
        if "password" in user:
            user.pop("password", None)
            mutated = True
        return mutated

    plaintext = user.pop("password", None)
    if plaintext:
        password_hash, password_salt = hash_password(plaintext)
        user["password_hash"] = password_hash
        user["password_salt"] = password_salt
        mutated = True

    return mutated
