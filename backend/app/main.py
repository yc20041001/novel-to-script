from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.auth import router as auth_router
from app.config import get_settings
from app.models import (
    GenerateRequest,
    GenerateResponse,
    ScriptDocument,
    ValidateYamlRequest,
    ValidateYamlResponse,
)
from app.services.deepseek_service import DeepSeekError, generate_script_with_deepseek
from app.services.mock_service import build_mock_script
from app.services.yaml_service import script_to_yaml, validate_yaml

settings = get_settings()


async def init_session_store(app: FastAPI) -> None:
    from app.session_store import InMemorySessionStore, RedisSessionStore

    try:
        store = RedisSessionStore(settings.redis_url)
        await store.ping()
        app.state.session_store = store
    except Exception:
        print("⚠ Redis 不可用，使用内存 session 存储（重启后登录失效）")
        app.state.session_store = InMemorySessionStore()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_session_store(app)
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


@app.get("/api/health")
async def health() -> dict:
    return {"status": "ok", "service": "novel2script-api"}


@app.get("/api/schema")
async def schema() -> dict:
    return ScriptDocument.model_json_schema()


@app.post("/api/generate", response_model=GenerateResponse)
async def generate(request: GenerateRequest) -> GenerateResponse:
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

    return GenerateResponse(script=script, yaml=script_to_yaml(script), used_mock=used_mock)


@app.post("/api/validate-yaml", response_model=ValidateYamlResponse)
async def validate_yaml_endpoint(request: ValidateYamlRequest) -> ValidateYamlResponse:
    valid, errors = validate_yaml(request.yaml)
    return ValidateYamlResponse(valid=valid, errors=errors)
