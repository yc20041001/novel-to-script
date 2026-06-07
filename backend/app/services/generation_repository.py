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

    @abc.abstractmethod
    async def admin_stats(self) -> dict[str, Any]: ...

    @abc.abstractmethod
    async def list_generation_records(self, limit: int = 50) -> list[dict[str, Any]]: ...


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

    async def admin_stats(self) -> dict[str, Any]:
        return {
            "project_count": 0,
            "generation_count": 0,
            "script_version_count": 0,
            "generated_script_count": 0,
            "mock_generation_count": 0,
        }

    async def list_generation_records(self, limit: int = 50) -> list[dict[str, Any]]:
        return []


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

    async def admin_stats(self) -> dict[str, Any]:
        return {
            "project_count": len(self._store),
            "generation_count": len(self._store),
            "script_version_count": len(self._store),
            "generated_script_count": len(self._store),
            "mock_generation_count": sum(1 for item in self._store.values() if item.get("used_mock")),
        }

    async def list_generation_records(self, limit: int = 50) -> list[dict[str, Any]]:
        records = []
        for index, (cache_key, payload) in enumerate(self._store.items(), start=1):
            script = payload.get("script", {})
            source = script.get("source", {})
            metadata = script.get("metadata", {})
            yaml_text = payload.get("yaml", "")
            records.append(
                {
                    "id": index,
                    "cache_key": cache_key,
                    "project_id": None,
                    "project_title": metadata.get("title") or "未命名项目",
                    "chapter_count": source.get("chapter_count", 0),
                    "model_name": "memory",
                    "used_mock": bool(payload.get("used_mock")),
                    "yaml_line_count": len(yaml_text.splitlines()),
                    "created_at": None,
                    "updated_at": None,
                }
            )
        return records[:limit]


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
                    CREATE TABLE IF NOT EXISTS projects (
                        id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
                        title VARCHAR(200) NOT NULL,
                        description TEXT NULL,
                        status VARCHAR(32) NOT NULL DEFAULT 'completed',
                        source_type VARCHAR(32) NOT NULL DEFAULT 'generate_request',
                        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                        INDEX idx_projects_created_at (created_at)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                    """
                )
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS chapters (
                        id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
                        project_id BIGINT UNSIGNED NOT NULL,
                        chapter_order INT NOT NULL,
                        title VARCHAR(255) NOT NULL,
                        content LONGTEXT NOT NULL,
                        content_length INT NOT NULL DEFAULT 0,
                        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                        UNIQUE KEY uk_chapters_project_order (project_id, chapter_order),
                        INDEX idx_chapters_project_id (project_id),
                        CONSTRAINT fk_chapters_project
                            FOREIGN KEY (project_id) REFERENCES projects(id)
                            ON DELETE CASCADE
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                    """
                )
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS generation_jobs (
                        id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
                        project_id BIGINT UNSIGNED NOT NULL,
                        cache_key VARCHAR(96) NOT NULL,
                        status VARCHAR(32) NOT NULL DEFAULT 'success',
                        model_provider VARCHAR(32) NOT NULL DEFAULT 'deepseek',
                        model_name VARCHAR(100) NOT NULL,
                        request_json JSON NOT NULL,
                        used_mock BOOLEAN NOT NULL DEFAULT FALSE,
                        started_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        finished_at TIMESTAMP NULL,
                        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        INDEX idx_generation_jobs_project_id (project_id),
                        INDEX idx_generation_jobs_cache_key (cache_key),
                        CONSTRAINT fk_generation_jobs_project
                            FOREIGN KEY (project_id) REFERENCES projects(id)
                            ON DELETE CASCADE
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                    """
                )
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS script_versions (
                        id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
                        project_id BIGINT UNSIGNED NOT NULL,
                        generation_job_id BIGINT UNSIGNED NOT NULL,
                        version_name VARCHAR(100) NOT NULL DEFAULT 'AI 初稿',
                        script_json JSON NOT NULL,
                        yaml_text LONGTEXT NOT NULL,
                        is_latest BOOLEAN NOT NULL DEFAULT TRUE,
                        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                        INDEX idx_script_versions_project_id (project_id),
                        INDEX idx_script_versions_generation_job_id (generation_job_id),
                        CONSTRAINT fk_script_versions_project
                            FOREIGN KEY (project_id) REFERENCES projects(id)
                            ON DELETE CASCADE,
                        CONSTRAINT fk_script_versions_generation_job
                            FOREIGN KEY (generation_job_id) REFERENCES generation_jobs(id)
                            ON DELETE CASCADE
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                    """
                )
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS generated_scripts (
                        id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
                        cache_key VARCHAR(96) NOT NULL UNIQUE,
                        project_id BIGINT UNSIGNED NULL,
                        generation_job_id BIGINT UNSIGNED NULL,
                        script_version_id BIGINT UNSIGNED NULL,
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
                self._ensure_generated_scripts_columns(cursor)
            conn.commit()
        finally:
            conn.close()

    def _ensure_generated_scripts_columns(self, cursor) -> None:
        cursor.execute("SHOW COLUMNS FROM generated_scripts")
        columns = {row["Field"] for row in cursor.fetchall()}
        additions = {
            "project_id": "ADD COLUMN project_id BIGINT UNSIGNED NULL AFTER cache_key",
            "generation_job_id": "ADD COLUMN generation_job_id BIGINT UNSIGNED NULL AFTER project_id",
            "script_version_id": "ADD COLUMN script_version_id BIGINT UNSIGNED NULL AFTER generation_job_id",
        }
        for column, ddl in additions.items():
            if column not in columns:
                cursor.execute(f"ALTER TABLE generated_scripts {ddl}")

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
                project_id = self._insert_project(cursor, request_payload, response_payload)
                self._insert_chapters(cursor, project_id, request_payload)
                generation_job_id = self._insert_generation_job(
                    cursor,
                    project_id,
                    cache_key,
                    request_json,
                    response_payload,
                )
                script_version_id = self._insert_script_version(
                    cursor,
                    project_id,
                    generation_job_id,
                    response_payload,
                )
                cursor.execute(
                    """
                    INSERT INTO generated_scripts
                        (
                            cache_key,
                            project_id,
                            generation_job_id,
                            script_version_id,
                            request_json,
                            response_json,
                            yaml_text,
                            used_mock
                        )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                        project_id = VALUES(project_id),
                        generation_job_id = VALUES(generation_job_id),
                        script_version_id = VALUES(script_version_id),
                        response_json = VALUES(response_json),
                        yaml_text = VALUES(yaml_text),
                        used_mock = VALUES(used_mock)
                    """,
                    (
                        cache_key,
                        project_id,
                        generation_job_id,
                        script_version_id,
                        request_json,
                        response_json,
                        response_payload["yaml"],
                        response_payload["used_mock"],
                    ),
                )
            conn.commit()
        finally:
            conn.close()

    def _insert_project(
        self,
        cursor,
        request_payload: dict[str, Any],
        response_payload: dict[str, Any],
    ) -> int:
        metadata = response_payload.get("script", {}).get("metadata", {})
        chapters = request_payload.get("chapters", [])
        fallback_title = chapters[0]["title"] if chapters else "未命名项目"
        title = metadata.get("title") or fallback_title
        description = metadata.get("logline") or None
        cursor.execute(
            """
            INSERT INTO projects (title, description, status, source_type)
            VALUES (%s, %s, %s, %s)
            """,
            (title, description, "completed", "generate_request"),
        )
        return cursor.lastrowid

    def _insert_chapters(self, cursor, project_id: int, request_payload: dict[str, Any]) -> None:
        for index, chapter in enumerate(request_payload.get("chapters", []), start=1):
            content = chapter["content"]
            cursor.execute(
                """
                INSERT INTO chapters (project_id, chapter_order, title, content, content_length)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (project_id, index, chapter["title"], content, len(content)),
            )

    def _insert_generation_job(
        self,
        cursor,
        project_id: int,
        cache_key: str,
        request_json: str,
        response_payload: dict[str, Any],
    ) -> int:
        used_mock = bool(response_payload.get("used_mock"))
        cursor.execute(
            """
            INSERT INTO generation_jobs
                (project_id, cache_key, status, model_provider, model_name, request_json, used_mock, finished_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
            """,
            (
                project_id,
                cache_key,
                "success",
                "mock" if used_mock else "deepseek",
                "mock" if used_mock else self._settings.deepseek_model,
                request_json,
                used_mock,
            ),
        )
        return cursor.lastrowid

    def _insert_script_version(
        self,
        cursor,
        project_id: int,
        generation_job_id: int,
        response_payload: dict[str, Any],
    ) -> int:
        cursor.execute(
            """
            INSERT INTO script_versions
                (project_id, generation_job_id, version_name, script_json, yaml_text, is_latest)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (
                project_id,
                generation_job_id,
                "AI 初稿",
                json.dumps(response_payload["script"], ensure_ascii=False),
                response_payload["yaml"],
                True,
            ),
        )
        return cursor.lastrowid

    async def admin_stats(self) -> dict[str, Any]:
        return await asyncio.to_thread(self._admin_stats_sync)

    def _admin_stats_sync(self) -> dict[str, Any]:
        conn = self._connect()
        try:
            with conn.cursor() as cursor:
                return {
                    "project_count": self._count_table(cursor, "projects"),
                    "generation_count": self._count_table(cursor, "generation_jobs"),
                    "script_version_count": self._count_table(cursor, "script_versions"),
                    "generated_script_count": self._count_table(cursor, "generated_scripts"),
                    "mock_generation_count": self._count_where(cursor, "generation_jobs", "used_mock = TRUE"),
                }
        finally:
            conn.close()

    def _count_table(self, cursor, table: str) -> int:
        cursor.execute(f"SELECT COUNT(*) AS count FROM {table}")
        return int(cursor.fetchone()["count"])

    def _count_where(self, cursor, table: str, condition: str) -> int:
        cursor.execute(f"SELECT COUNT(*) AS count FROM {table} WHERE {condition}")
        return int(cursor.fetchone()["count"])

    async def list_generation_records(self, limit: int = 50) -> list[dict[str, Any]]:
        return await asyncio.to_thread(self._list_generation_records_sync, limit)

    def _list_generation_records_sync(self, limit: int = 50) -> list[dict[str, Any]]:
        conn = self._connect()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT
                        gs.id,
                        gs.cache_key,
                        gs.project_id,
                        p.title AS project_title,
                        COUNT(c.id) AS chapter_count,
                        gj.model_name,
                        gs.used_mock,
                        gs.yaml_text,
                        gs.created_at,
                        gs.updated_at
                    FROM generated_scripts gs
                    LEFT JOIN projects p ON p.id = gs.project_id
                    LEFT JOIN generation_jobs gj ON gj.id = gs.generation_job_id
                    LEFT JOIN chapters c ON c.project_id = gs.project_id
                    GROUP BY
                        gs.id,
                        gs.cache_key,
                        gs.project_id,
                        p.title,
                        gj.model_name,
                        gs.used_mock,
                        gs.yaml_text,
                        gs.created_at,
                        gs.updated_at
                    ORDER BY gs.created_at DESC
                    LIMIT %s
                    """,
                    (limit,),
                )
                return [self._serialize_generation_record(row) for row in cursor.fetchall()]
        finally:
            conn.close()

    def _serialize_generation_record(self, row: dict[str, Any]) -> dict[str, Any]:
        yaml_text = row.pop("yaml_text") or ""
        result = dict(row)
        result["used_mock"] = bool(result.get("used_mock"))
        result["yaml_line_count"] = len(yaml_text.splitlines())
        for field in ("created_at", "updated_at"):
            if result.get(field) is not None:
                result[field] = result[field].isoformat(sep=" ")
        return result
