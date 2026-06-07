from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.admin import router as admin_router
from app.auth import router as auth_router
from app.config import get_settings
from app.models import (
    GenerateRequest,
    GenerateResponse,
    ScriptDocument,
    ValidateYamlRequest,
    ValidateYamlResponse,
)
from app.services.generation_cache_service import (
    InMemoryGenerationCache,
    RedisGenerationCache,
    build_generation_cache_key,
)
from app.services.deepseek_service import DeepSeekError, generate_script_with_deepseek
from app.services.generation_repository import MySQLGenerationRepository, NoopGenerationRepository
from app.services.mock_service import build_mock_script
from app.services.user_repository import InMemoryUserRepository, MySQLUserRepository
from app.services.yaml_service import script_to_yaml, validate_yaml

settings = get_settings()


async def init_session_store(app: FastAPI) -> None:
    from app.session_store import InMemorySessionStore, RedisSessionStore

    try:
        store = RedisSessionStore(
            settings.redis_url,
            password=settings.redis_password or None,
        )
        await store.ping()
        app.state.session_store = store
        print("✓ Redis session store connected")
    except Exception as exc:
        print(f"⚠ Redis 不可用，使用内存 session 存储（重启后登录失效）：{exc.__class__.__name__}")
        app.state.session_store = InMemorySessionStore()


async def init_captcha_store(app: FastAPI) -> None:
    from app.captcha_store import InMemoryCaptchaStore, RedisCaptchaStore

    try:
        store = RedisCaptchaStore(
            settings.redis_url,
            password=settings.redis_password or None,
        )
        await store.ping()
        app.state.captcha_store = store
        print("✓ Redis captcha store connected")
    except Exception as exc:
        print(f"⚠ Redis 验证码存储不可用，使用内存验证码：{exc.__class__.__name__}")
        app.state.captcha_store = InMemoryCaptchaStore()


async def init_generation_cache(app: FastAPI) -> None:
    try:
        cache = RedisGenerationCache(
            settings.redis_url,
            password=settings.redis_password or None,
        )
        await cache.ping()
        app.state.generation_cache = cache
        print("✓ Redis generation cache connected")
    except Exception as exc:
        print(f"⚠ Redis 生成缓存不可用，使用内存缓存：{exc.__class__.__name__}")
        app.state.generation_cache = InMemoryGenerationCache()


async def init_generation_repository(app: FastAPI) -> None:
    try:
        repository = MySQLGenerationRepository(settings)
        await repository.init()
        app.state.generation_repository = repository
        print("✓ MySQL generation repository connected")
    except Exception as exc:
        print(f"⚠ MySQL 生成结果落库不可用，跳过数据库保存：{exc.__class__.__name__}")
        app.state.generation_repository = NoopGenerationRepository()


async def init_user_repository(app: FastAPI) -> None:
    try:
        repository = MySQLUserRepository(settings)
        await repository.init()
        app.state.user_repository = repository
        print("✓ MySQL user repository connected")
    except Exception as exc:
        print(f"⚠ MySQL 用户表不可用，使用内存 demo 用户：{exc.__class__.__name__}")
        repository = InMemoryUserRepository(settings)
        await repository.init()
        app.state.user_repository = repository


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_session_store(app)
    await init_captcha_store(app)
    await init_generation_cache(app)
    await init_generation_repository(app)
    await init_user_repository(app)
    yield


app = FastAPI(
    title="Novel2Script API",
    description="AI 小说转结构化剧本工具后端 API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.frontend_origin,
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(admin_router)


@app.get("/api/health")
async def health() -> dict:
    return {"status": "ok", "service": "novel2script-api"}


@app.get("/api/schema")
async def schema() -> dict:
    return ScriptDocument.model_json_schema()


@app.post("/api/generate", response_model=GenerateResponse)
async def generate(request: GenerateRequest) -> GenerateResponse:
    cache_key = build_generation_cache_key(request)
    cache = getattr(app.state, "generation_cache", InMemoryGenerationCache())
    repository = getattr(app.state, "generation_repository", NoopGenerationRepository())

    cached_payload = await cache.get(cache_key)
    if cached_payload is not None:
        cached_payload["cache_hit"] = True
        cached_payload["cache_key"] = cache_key
        cached_payload["storage"] = "redis"
        return GenerateResponse.model_validate(cached_payload)

    persisted_payload = await repository.get(cache_key)
    if persisted_payload is not None:
        persisted_payload["cache_hit"] = True
        persisted_payload["cache_key"] = cache_key
        persisted_payload["storage"] = "mysql"
        await cache.set(cache_key, persisted_payload, settings.generation_cache_ttl_seconds)
        return GenerateResponse.model_validate(persisted_payload)

    used_mock = False
    try:
        script = await generate_script_with_deepseek(
            request.chapters,
            settings,
            request.options,
        )
    except DeepSeekError:
        used_mock = True
        script = build_mock_script([chapter.title for chapter in request.chapters])

    response = GenerateResponse(
        script=script,
        yaml=script_to_yaml(script),
        used_mock=used_mock,
        cache_hit=False,
        cache_key=cache_key,
        storage="generated",
    )
    response_payload = response.model_dump(mode="json")
    await cache.set(cache_key, response_payload, settings.generation_cache_ttl_seconds)
    await repository.save(
        cache_key,
        request.model_dump(mode="json"),
        response_payload,
    )
    return response


@app.post("/api/validate-yaml", response_model=ValidateYamlResponse)
async def validate_yaml_endpoint(request: ValidateYamlRequest) -> ValidateYamlResponse:
    valid, errors = validate_yaml(request.yaml)
    return ValidateYamlResponse(valid=valid, errors=errors)
