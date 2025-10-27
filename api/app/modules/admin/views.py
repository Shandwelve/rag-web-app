from typing import Annotated

from fastapi import APIRouter, Depends
from sqlmodel import func, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.database import get_db_session
from app.modules.admin.schema import AdminStats
from app.modules.auth.middleware import get_current_admin_user
from app.modules.auth.models import User
from app.modules.auth.repository import UserRepository
from app.modules.files.models import File

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/stats", response_model=AdminStats)
async def get_admin_stats(
    current_user: Annotated[User, Depends(get_current_admin_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
    user_repository: Annotated[UserRepository, Depends(UserRepository)],
) -> AdminStats:
    total_users = await user_repository.count()

    file_count_stmt = select(func.count()).select_from(File)
    file_count_result = await session.exec(file_count_stmt)
    total_files = file_count_result.first() or 0

    return AdminStats(
        total_users=total_users,
        total_files=total_files,
        recent_activity=[],
    )
