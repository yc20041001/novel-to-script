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

    @abc.abstractmethod
    async def create_user(
        self,
        username: str,
        password: str,
        display_name: str | None = None,
    ) -> dict[str, Any]: ...

    @abc.abstractmethod
    async def list_users(self) -> list[dict[str, Any]]: ...

    @abc.abstractmethod
    async def update_user(
        self,
        user_id: int,
        *,
        role: str | None = None,
        status: str | None = None,
    ) -> dict[str, Any] | None: ...


class InMemoryUserRepository(UserRepository):
    def __init__(self, settings: Settings) -> None:
        self._users = {
            settings.demo_username: {
                "id": 1,
                "username": settings.demo_username,
                "password_hash": hash_password(settings.demo_password),
                "display_name": settings.demo_username,
                "role": "admin",
                "status": "active",
                "created_at": None,
                "updated_at": None,
            }
        }

    async def init(self) -> None:
        return None

    async def verify_user(self, username: str, password: str) -> dict[str, Any] | None:
        user = self._users.get(username)
        if (
            user is None
            or user.get("status", "active") != "active"
            or not verify_password(password, user["password_hash"])
        ):
            return None
        return {k: v for k, v in user.items() if k != "password_hash"}

    async def create_user(
        self,
        username: str,
        password: str,
        display_name: str | None = None,
    ) -> dict[str, Any]:
        if username in self._users:
            raise ValueError("用户名已存在")
        user = {
            "id": len(self._users) + 1,
            "username": username,
            "password_hash": hash_password(password),
            "display_name": display_name or username,
            "role": "author",
            "status": "active",
            "created_at": None,
            "updated_at": None,
        }
        self._users[username] = user
        return {k: v for k, v in user.items() if k != "password_hash"}

    async def list_users(self) -> list[dict[str, Any]]:
        users = [
            {k: v for k, v in user.items() if k != "password_hash"}
            for user in self._users.values()
        ]
        return sorted(users, key=lambda user: user["id"] or 0)

    async def update_user(
        self,
        user_id: int,
        *,
        role: str | None = None,
        status: str | None = None,
    ) -> dict[str, Any] | None:
        for user in self._users.values():
            if user["id"] == user_id:
                if role is not None:
                    user["role"] = role
                if status is not None:
                    user["status"] = status
                return {k: v for k, v in user.items() if k != "password_hash"}
        return None


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
                        status VARCHAR(32) NOT NULL DEFAULT 'active',
                        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                    """
                )
                self._ensure_users_columns(cursor)
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

    def _ensure_users_columns(self, cursor) -> None:
        cursor.execute("SHOW COLUMNS FROM users")
        columns = {row["Field"] for row in cursor.fetchall()}
        if "status" not in columns:
            cursor.execute("ALTER TABLE users ADD COLUMN status VARCHAR(32) NOT NULL DEFAULT 'active' AFTER role")

    async def verify_user(self, username: str, password: str) -> dict[str, Any] | None:
        return await asyncio.to_thread(self._verify_user_sync, username, password)

    def _verify_user_sync(self, username: str, password: str) -> dict[str, Any] | None:
        conn = self._connect()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT id, username, password_hash, display_name, role, status
                    FROM users
                    WHERE username = %s
                    """,
                    (username,),
                )
                user = cursor.fetchone()
                if (
                    user is None
                    or user.get("status", "active") != "active"
                    or not verify_password(password, user["password_hash"])
                ):
                    return None
                return {k: v for k, v in user.items() if k != "password_hash"}
        finally:
            conn.close()

    async def create_user(
        self,
        username: str,
        password: str,
        display_name: str | None = None,
    ) -> dict[str, Any]:
        return await asyncio.to_thread(self._create_user_sync, username, password, display_name)

    def _create_user_sync(
        self,
        username: str,
        password: str,
        display_name: str | None = None,
    ) -> dict[str, Any]:
        conn = self._connect()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
                if cursor.fetchone() is not None:
                    raise ValueError("用户名已存在")

                cursor.execute(
                    """
                    INSERT INTO users (username, password_hash, display_name, role)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (username, hash_password(password), display_name or username, "author"),
                )
                user_id = cursor.lastrowid
            conn.commit()
            return {
                "id": user_id,
                "username": username,
                "display_name": display_name or username,
                "role": "author",
                "status": "active",
            }
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    async def list_users(self) -> list[dict[str, Any]]:
        return await asyncio.to_thread(self._list_users_sync)

    def _list_users_sync(self) -> list[dict[str, Any]]:
        conn = self._connect()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT id, username, display_name, role, status, created_at, updated_at
                    FROM users
                    ORDER BY id ASC
                    """
                )
                return [self._serialize_user(row) for row in cursor.fetchall()]
        finally:
            conn.close()

    async def update_user(
        self,
        user_id: int,
        *,
        role: str | None = None,
        status: str | None = None,
    ) -> dict[str, Any] | None:
        return await asyncio.to_thread(self._update_user_sync, user_id, role, status)

    def _update_user_sync(
        self,
        user_id: int,
        role: str | None = None,
        status: str | None = None,
    ) -> dict[str, Any] | None:
        updates = []
        params: list[Any] = []
        if role is not None:
            updates.append("role = %s")
            params.append(role)
        if status is not None:
            updates.append("status = %s")
            params.append(status)

        conn = self._connect()
        try:
            with conn.cursor() as cursor:
                if updates:
                    params.append(user_id)
                    cursor.execute(
                        f"UPDATE users SET {', '.join(updates)} WHERE id = %s",
                        tuple(params),
                    )
                    conn.commit()

                cursor.execute(
                    """
                    SELECT id, username, display_name, role, status, created_at, updated_at
                    FROM users
                    WHERE id = %s
                    """,
                    (user_id,),
                )
                row = cursor.fetchone()
                return self._serialize_user(row) if row else None
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def _serialize_user(self, row: dict[str, Any]) -> dict[str, Any]:
        result = dict(row)
        for field in ("created_at", "updated_at"):
            if result.get(field) is not None:
                result[field] = result[field].isoformat(sep=" ")
        return result
