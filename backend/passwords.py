import hashlib
import hmac

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerifyMismatchError

PASSWORD_HASHER = PasswordHasher(time_cost=3, memory_cost=65536, parallelism=2, hash_len=32, salt_len=16)


def legacy_hash(password, salt):
    return hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100_000, dklen=32).hex()


def hash_password(password):
    return PASSWORD_HASHER.hash(password)


def verify_password(stored_hash, password, salt=None):
    if not stored_hash:
        return False, None
    if stored_hash.startswith("$argon2"):
        try:
            ok = PASSWORD_HASHER.verify(stored_hash, password)
        except (VerifyMismatchError, InvalidHashError):
            return False, None
        return bool(ok), PASSWORD_HASHER.hash(password) if ok and PASSWORD_HASHER.check_needs_rehash(stored_hash) else None
    candidate = legacy_hash(password, salt or "tyvon-invalid-login-salt")
    if not hmac.compare_digest(candidate, stored_hash):
        return False, None
    return True, PASSWORD_HASHER.hash(password)
