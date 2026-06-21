from bcrypt import gensalt, hashpw, checkpw


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    hashed = hashpw(password.encode("utf-8"), gensalt())
    return hashed.decode("utf-8")

def check_password(password: str, hashed: str) -> bool:
    """Check a password against a hashed value."""
    return checkpw(password.encode("utf-8"), hashed.encode("utf-8"))
