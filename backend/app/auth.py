from fastapi import APIRouter, HTTPException, Request
from starlette.responses import JSONResponse

from app.config import get_settings
from app.models import LoginRequest

router = APIRouter(tags=["auth"])


def _get_store(request: Request):
    return request.app.state.session_store


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


@router.post("/api/auth/login")
async def login(request: Request, body: LoginRequest) -> JSONResponse:
    settings = get_settings()

    user = await _verify_user(request, body)
    if user is None:
        raise HTTPException(status_code=401, detail="用户名或密码错误")

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
