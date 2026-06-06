from fastapi import APIRouter, HTTPException, Request
from starlette.responses import JSONResponse

from app.config import get_settings
from app.models import LoginRequest

router = APIRouter(tags=["auth"])


def _get_store(request: Request):
    return request.app.state.session_store


@router.post("/api/auth/login")
async def login(request: Request, body: LoginRequest) -> JSONResponse:
    settings = get_settings()

    if body.username != settings.demo_username or body.password != settings.demo_password:
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    store = _get_store(request)
    session_id = await store.create_session(
        {"username": body.username},
        settings.session_ttl_seconds,
    )

    content = {"authenticated": True, "user": {"username": body.username}}
    resp = JSONResponse(content=content, status_code=200)
    resp.set_cookie(
        key=settings.session_cookie_name,
        value=session_id,
        httponly=True,
        samesite="lax",
        secure=False,
        max_age=settings.session_ttl_seconds,
    )
    return resp


@router.get("/api/auth/me")
async def me(request: Request) -> dict:
    settings = get_settings()
    session_id = request.cookies.get(settings.session_cookie_name)
    if not session_id:
        return {"authenticated": False}

    store = _get_store(request)
    data = await store.get_session(session_id)
    if data is None:
        return {"authenticated": False}

    return {"authenticated": True, "user": {"username": data["username"]}}


@router.post("/api/auth/logout")
async def logout(request: Request) -> JSONResponse:
    settings = get_settings()
    session_id = request.cookies.get(settings.session_cookie_name)
    if session_id:
        store = _get_store(request)
        await store.delete_session(session_id)

    resp = JSONResponse(content={"authenticated": False})
    resp.delete_cookie(
        key=settings.session_cookie_name,
        httponly=True,
        samesite="lax",
        secure=False,
    )
    return resp
