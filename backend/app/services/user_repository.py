import abc
import asyncio
import hashlib
import secrets
from typing import Any

from app.config import Settings


def hash_password(password: str, *, salt: str | None = None, iterations: int = 120_000) -> str:
    salt = salt or secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        iterations,
    ).hex()
    return f"pbkdf2_sha256${iterations}${salt}${digest}"


def verify_password(password: str, encoded: str) -> bool:
    try:
        algorithm, iterations_raw, salt, expected = encoded.split("$", 3)
        if algorithm != "pbkdf2_sha256":
            return False
        iterations = int(iterations_raw)
    except ValueError:
        return False

    actual = hash_password(password, salt=salt, iterations=iterations).split("$", 3)[3]
    return secrets.compare_digest(actual, expected)


class UserRepository(abc.ABC):
    @abc.abstractmethod
    async def init(self) -> None: ...

    @abc.abstractmethod
    async def verify_user(self, username: str, password: str) -> dict[str, Any] | None: ...


class InMemoryUserRepository(UserRepository):
    def __init__(self, settings: Settings) -> None:
        self._users = {
            settings.demo_username: {
                "id": 1,
                "username": settings.demo_username,
                "password_hash": hash_password(settings.demo_password),
                "display_name": settings.demo_username,
                "role": "admin",
            }
        }

    async def init(self) -> None:
        return None

    async def verify_user(self, username: str, password: str) -> dict[str, Any] | None:
        user = self._users.get(username)
        if user is None or not verify_password(password, user["password_hash"]):
            return None
        return {k: v for k, v in user.items() if k != "password_hash"}


class MySQLUserRepository(UserRepository):
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    def _connect(self, *, with_database: bool = True):
        import pymysql

        return pymysql.connect(
            host=self._settings.mysql_host,
            port=self._settings.mysql_port,
            user=self._settings.mysql_user,
            password=self._settings.mysql_password,
            database=self._settings.mysql_database if with_database else None,
            charset="utf8mb4",
            autocommit=False,
            cursorclass=pymysql.cursors.DictCursor,
        )

    async def init(self) -> None:
        await asyncio.to_thread(self._init_sync)

    def _init_sync(self) -> None:
        conn = self._connect(with_database=False)
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    f"CREATE DATABASE IF NOT EXISTS `{self._settings.mysql_database}` "
                    "DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
                )
            conn.commit()
        finally:
            conn.close()

        conn = self._connect()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS users (
                        id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
                        username VARCHAR(64) NOT NULL UNIQUE,
                        password_hash VARCHAR(255) NOT NULL,
                        display_name VARCHAR(100) NOT NULL,
                        role VARCHAR(32) NOT NULL DEFAULT 'author',
                        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                    """
                )
                cursor.execute("SELECT id FROM users WHERE username = %s", (self._settings.demo_username,))
                if cursor.fetchone() is None:
                    cursor.execute(
                        """
                        INSERT INTO users (username, password_hash, display_name, role)
                        VALUES (%s, %s, %s, %s)
                        """,
                        (
                            self._settings.demo_username,
                            hash_password(self._settings.demo_password),
                            self._settings.demo_username,
                            "admin",
                        ),
                    )
            conn.commit()
        finally:
            conn.close()

    async def verify_user(self, username: str, password: str) -> dict[str, Any] | None:
        return await asyncio.to_thread(self._verify_user_sync, username, password)

    def _verify_user_sync(self, username: str, password: str) -> dict[str, Any] | None:
        conn = self._connect()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT id, username, password_hash, display_name, role
                    FROM users
                    WHERE username = %s
                    """,
                    (username,),
                )
                user = cursor.fetchone()
                if user is None or not verify_password(password, user["password_hash"]):
                    return None
                return {k: v for k, v in user.items() if k != "password_hash"}
        finally:
            conn.close()
