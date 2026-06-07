from fastapi import APIRouter, HTTPException, Request
from starlette.responses import JSONResponse

from app.config import get_settings
from app.models import CaptchaResponse, LoginRequest, RegisterRequest

router = APIRouter(tags=["auth"])


def _get_store(request: Request):
    return request.app.state.session_store


def _get_captcha_store(request: Request):
    return request.app.state.captcha_store


async def _verify_user(request: Request, body: LoginRequest) -> dict | None:
    user_repository = getattr(request.app.state, "user_repository", None)
    if user_repository is not None:
        return await user_repository.verify_user(body.username, body.password)

    settings = get_settings()
    if body.username == settings.demo_username and body.password == settings.demo_password:
        return {
            "id": None,
            "username": body.username,
            "display_name": body.username,
            "role": "admin",
        }
    return None


async def _verify_captcha(request: Request, captcha_id: str, captcha_code: str) -> None:
    captcha_store = _get_captcha_store(request)
    is_valid = await captcha_store.verify_captcha(captcha_id, captcha_code)
    if not is_valid:
        raise HTTPException(status_code=400, detail="验证码错误或已过期")


async def _create_auth_response(request: Request, user: dict) -> JSONResponse:
    settings = get_settings()
    store = _get_store(request)
    session_id = await store.create_session(
        {
            "user_id": user.get("id"),
            "username": user["username"],
            "display_name": user.get("display_name") or user["username"],
            "role": user.get("role") or "author",
        },
        settings.session_ttl_seconds,
    )

    content = {
        "authenticated": True,
        "user": {
            "username": user["username"],
            "display_name": user.get("display_name") or user["username"],
            "role": user.get("role") or "author",
        },
    }
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


@router.get("/api/auth/captcha", response_model=CaptchaResponse)
async def captcha(request: Request) -> CaptchaResponse:
    settings = get_settings()
    captcha_store = _get_captcha_store(request)
    payload = await captcha_store.create_captcha(settings.captcha_ttl_seconds)
    return CaptchaResponse(**payload)


@router.post("/api/auth/login")
async def login(request: Request, body: LoginRequest) -> JSONResponse:
    await _verify_captcha(request, body.captcha_id, body.captcha_code)

    user = await _verify_user(request, body)
    if user is None:
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    return await _create_auth_response(request, user)


@router.post("/api/auth/register")
async def register(request: Request, body: RegisterRequest) -> JSONResponse:
    await _verify_captcha(request, body.captcha_id, body.captcha_code)

    user_repository = getattr(request.app.state, "user_repository", None)
    if user_repository is None:
        raise HTTPException(status_code=503, detail="用户服务不可用")

    try:
        user = await user_repository.create_user(
            body.username.strip(),
            body.password,
            body.display_name.strip() if body.display_name else None,
        )
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc

    return await _create_auth_response(request, user)


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

    return {
        "authenticated": True,
        "user": {
            "username": data["username"],
            "display_name": data.get("display_name") or data["username"],
            "role": data.get("role") or "author",
        },
    }


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
