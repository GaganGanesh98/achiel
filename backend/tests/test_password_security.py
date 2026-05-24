from app.core._security_base import hash_password, verify_password


def test_hash_password_normal_length() -> None:
    password = "shortpass12"
    hashed = hash_password(password)
    assert hashed.startswith("$2")
    assert verify_password(password, hashed)


def test_hash_password_100_chars() -> None:
    password = "a" * 100
    hashed = hash_password(password)
    assert verify_password(password, hashed)


def test_hash_password_multibyte_over_72_bytes() -> None:
    # 24 × "ä" (2 bytes each) = 48 bytes; 12 × "🎓" (4 bytes each) = 48 → 96 bytes total
    password = "ä" * 24 + "🎓" * 12
    assert len(password.encode("utf-8")) > 72
    hashed = hash_password(password)
    assert verify_password(password, hashed)
