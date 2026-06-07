from fastapi import APIRouter, HTTPException, Query, Request

from app.config import get_settings
from app.models import (
    AdminGenerationRecord,
    AdminGenerationRecordsResponse,
    AdminStatsResponse,
    AdminUpdateUserRequest,
    AdminUserItem,
    AdminUsersResponse,
)
from app.services.generation_repository import NoopGenerationRepository

router = APIRouter(prefix="/api/admin", tags=["admin"])


async def _require_admin(request: Request) -> dict:
    settings = get_settings()
    session_id = request.cookies.get(settings.session_cookie_name)
    if not session_id:
        raise HTTPException(status_code=401, detail="请先登录")

    session_store = request.app.state.session_store
    session = await session_store.get_session(session_id)
    if session is None:
        raise HTTPException(status_code=401, detail="登录已过期")
    if session.get("role") != "admin":
        raise HTTPException(status_code=403, detail="需要管理员权限")
    return session


def _user_count_stats(users: list[dict]) -> dict:
    return {
        "user_count": len(users),
        "active_user_count": sum(1 for user in users if user.get("status", "active") == "active"),
    }


@router.get("/stats", response_model=AdminStatsResponse)
async def admin_stats(request: Request) -> AdminStatsResponse:
    await _require_admin(request)
    user_repository = request.app.state.user_repository
    generation_repository = getattr(
        request.app.state,
        "generation_repository",
        NoopGenerationRepository(),
    )

    users = await user_repository.list_users()
    generation_stats = await generation_repository.admin_stats()
    return AdminStatsResponse(**_user_count_stats(users), **generation_stats)


@router.get("/users", response_model=AdminUsersResponse)
async def admin_users(request: Request) -> AdminUsersResponse:
    await _require_admin(request)
    user_repository = request.app.state.user_repository
    users = await user_repository.list_users()
    return AdminUsersResponse(users=[AdminUserItem(**user) for user in users])


@router.patch("/users/{user_id}", response_model=AdminUserItem)
async def admin_update_user(
    user_id: int,
    body: AdminUpdateUserRequest,
    request: Request,
) -> AdminUserItem:
    session = await _require_admin(request)
    if body.role is not None and body.role not in {"admin", "author"}:
        raise HTTPException(status_code=422, detail="角色只能是 admin 或 author")
    if body.status is not None and body.status not in {"active", "disabled"}:
        raise HTTPException(status_code=422, detail="状态只能是 active 或 disabled")
    if body.status == "disabled" and session.get("user_id") == user_id:
        raise HTTPException(status_code=400, detail="不能禁用当前登录的管理员")

    user_repository = request.app.state.user_repository
    user = await user_repository.update_user(user_id, role=body.role, status=body.status)
    if user is None:
        raise HTTPException(status_code=404, detail="用户不存在")
    return AdminUserItem(**user)


@router.get("/generations", response_model=AdminGenerationRecordsResponse)
async def admin_generations(
    request: Request,
    limit: int = Query(default=50, ge=1, le=200),
) -> AdminGenerationRecordsResponse:
    await _require_admin(request)
    generation_repository = getattr(
        request.app.state,
        "generation_repository",
        NoopGenerationRepository(),
    )
    records = await generation_repository.list_generation_records(limit)
    return AdminGenerationRecordsResponse(
        records=[AdminGenerationRecord(**record) for record in records]
    )
