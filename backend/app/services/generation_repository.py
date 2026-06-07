import abc
import asyncio
import json
from typing import Any

from app.config import Settings


class GenerationRepository(abc.ABC):
    @abc.abstractmethod
    async def init(self) -> None: ...

    @abc.abstractmethod
    async def get(self, cache_key: str) -> dict[str, Any] | None: ...

    @abc.abstractmethod
    async def save(
        self,
        cache_key: str,
        request_payload: dict[str, Any],
        response_payload: dict[str, Any],
    ) -> None: ...


class NoopGenerationRepository(GenerationRepository):
    async def init(self) -> None:
        return None

    async def get(self, cache_key: str) -> dict[str, Any] | None:
        return None

    async def save(
        self,
        cache_key: str,
        request_payload: dict[str, Any],
        response_payload: dict[str, Any],
    ) -> None:
        return None


class InMemoryGenerationRepository(GenerationRepository):
    def __init__(self) -> None:
        self._store: dict[str, dict[str, Any]] = {}

    async def init(self) -> None:
        return None

    async def get(self, cache_key: str) -> dict[str, Any] | None:
        return self._store.get(cache_key)

    async def save(
        self,
        cache_key: str,
        request_payload: dict[str, Any],
        response_payload: dict[str, Any],
    ) -> None:
        self._store[cache_key] = response_payload


class MySQLGenerationRepository(GenerationRepository):
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
            autocommit=True,
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
        finally:
            conn.close()

        conn = self._connect()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS generated_scripts (
                        id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
                        cache_key VARCHAR(96) NOT NULL UNIQUE,
                        request_json JSON NOT NULL,
                        response_json JSON NOT NULL,
                        yaml_text LONGTEXT NOT NULL,
                        used_mock BOOLEAN NOT NULL DEFAULT FALSE,
                        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                        INDEX idx_generated_scripts_created_at (created_at)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                    """
                )
        finally:
            conn.close()

    async def get(self, cache_key: str) -> dict[str, Any] | None:
        return await asyncio.to_thread(self._get_sync, cache_key)

    def _get_sync(self, cache_key: str) -> dict[str, Any] | None:
        conn = self._connect()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT response_json FROM generated_scripts WHERE cache_key = %s",
                    (cache_key,),
                )
                row = cursor.fetchone()
                if row is None:
                    return None
                raw = row["response_json"]
                return json.loads(raw) if isinstance(raw, str) else raw
        finally:
            conn.close()

    async def save(
        self,
        cache_key: str,
        request_payload: dict[str, Any],
        response_payload: dict[str, Any],
    ) -> None:
        await asyncio.to_thread(self._save_sync, cache_key, request_payload, response_payload)

    def _save_sync(
        self,
        cache_key: str,
        request_payload: dict[str, Any],
        response_payload: dict[str, Any],
    ) -> None:
        conn = self._connect()
        request_json = json.dumps(request_payload, ensure_ascii=False)
        response_json = json.dumps(response_payload, ensure_ascii=False)
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO generated_scripts
                        (cache_key, request_json, response_json, yaml_text, used_mock)
                    VALUES (%s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                        response_json = VALUES(response_json),
                        yaml_text = VALUES(yaml_text),
                        used_mock = VALUES(used_mock)
                    """,
                    (
                        cache_key,
                        request_json,
                        response_json,
                        response_payload["yaml"],
                        response_payload["used_mock"],
                    ),
                )
        finally:
            conn.close()
