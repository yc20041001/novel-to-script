import asyncio

from app.config import get_settings
from app.services.user_repository import InMemoryUserRepository, hash_password, verify_password


def test_password_hash_verification() -> None:
    encoded = hash_password("secret")
    assert verify_password("secret", encoded) is True
    assert verify_password("wrong", encoded) is False


def test_in_memory_user_repository_verifies_demo_user() -> None:
    settings = get_settings()
    repository = InMemoryUserRepository(settings)
    asyncio.run(repository.init())

    user = asyncio.run(repository.verify_user(settings.demo_username, settings.demo_password))
    assert user is not None
    assert user["username"] == settings.demo_username
    assert "password_hash" not in user


def test_in_memory_user_repository_creates_user() -> None:
    settings = get_settings()
    repository = InMemoryUserRepository(settings)
    asyncio.run(repository.init())

    created = asyncio.run(repository.create_user("writer", "secret123", "编剧"))
    assert created["username"] == "writer"
    assert created["display_name"] == "编剧"
    assert created["role"] == "author"

    verified = asyncio.run(repository.verify_user("writer", "secret123"))
    assert verified is not None
    assert verified["username"] == "writer"
