"""
用户管理API路由
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_active_user, get_user_locale
from app.core.i18n import get_i18n_manager
from app.schemas.user import UserUpdate, UserResponse
from app.schemas.common import ResponseModel, PaginatedResponse
from app.services.user_service import UserService
from app.models.user import User
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

router = APIRouter()


@router.get("/profile", response_model=UserResponse)
async def get_user_profile(
    current_user: User = Depends(get_current_active_user)
):
    """获取用户个人资料"""
    return current_user


@router.put("/profile", response_model=ResponseModel)
async def update_user_profile(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    locale: str = Depends(get_user_locale),
    i18n = Depends(get_i18n_manager)
):
    """更新用户个人资料"""
    try:
        user_service = UserService(db)
        updated_user = user_service.update_user(current_user.id, user_data)
        
        return ResponseModel(
            success=True,
            message=i18n.get_text("auth.profileUpdated", locale),
            data=updated_user.to_dict()
        )
        
    except Exception as e:
        logger.error(f"Profile update failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=i18n.get_text("auth.profileUpdateFailed", locale)
        )


@router.get("/", response_model=PaginatedResponse[UserResponse])
async def get_users(
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(10, ge=1, le=100, description="返回的记录数"),
    active_only: bool = Query(True, description="是否只返回活跃用户"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取用户列表（管理员功能）"""
    # 这里可以添加管理员权限检查
    # 目前简单实现，所有认证用户都可以查看
    
    user_service = UserService(db)
    users = user_service.get_users(skip=skip, limit=limit, active_only=active_only)
    total = user_service.count_users(active_only=active_only)
    
    pages = (total + limit - 1) // limit
    
    return PaginatedResponse(
        items=users,
        total=total,
        page=(skip // limit) + 1,
        size=limit,
        pages=pages,
        has_next=skip + limit < total,
        has_prev=skip > 0
    )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user_by_id(
    user_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    locale: str = Depends(get_user_locale),
    i18n = Depends(get_i18n_manager)
):
    """根据ID获取用户信息"""
    user_service = UserService(db)
    user = user_service.get_user_by_id(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=i18n.get_text("auth.userNotFound", locale)
        )
    
    return user


@router.delete("/{user_id}", response_model=ResponseModel)
async def deactivate_user(
    user_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    locale: str = Depends(get_user_locale),
    i18n = Depends(get_i18n_manager)
):
    """停用用户（管理员功能）"""
    # 防止用户删除自己
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=i18n.get_text("auth.cannotDeleteSelf", locale)
        )
    
    try:
        user_service = UserService(db)
        user_service.delete_user(user_id)
        
        return ResponseModel(
            success=True,
            message=i18n.get_text("auth.userDeactivated", locale)
        )
        
    except Exception as e:
        logger.error(f"User deactivation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=i18n.get_text("auth.userDeactivationFailed", locale)
        )


@router.post("/{user_id}/activate", response_model=ResponseModel)
async def activate_user(
    user_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    locale: str = Depends(get_user_locale),
    i18n = Depends(get_i18n_manager)
):
    """激活用户（管理员功能）"""
    try:
        user_service = UserService(db)
        user_service.activate_user(user_id)
        
        return ResponseModel(
            success=True,
            message=i18n.get_text("auth.userActivated", locale)
        )
        
    except Exception as e:
        logger.error(f"User activation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=i18n.get_text("auth.userActivationFailed", locale)
        )