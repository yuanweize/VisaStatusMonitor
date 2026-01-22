"""
FastAPI依赖项
"""

from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import verify_token
from app.models.user import User
from app.core.i18n import get_i18n_manager
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

# HTTP Bearer认证方案
security = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    获取当前认证用户
    
    Args:
        credentials: HTTP认证凭据
        db: 数据库会话
        
    Returns:
        当前用户对象
        
    Raises:
        HTTPException: 认证失败时抛出
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    if not credentials:
        raise credentials_exception
    
    # 验证令牌
    payload = verify_token(credentials.credentials)
    if not payload:
        raise credentials_exception
    
    # 获取用户ID
    user_id: str = payload.get("sub")
    if user_id is None:
        raise credentials_exception
    
    try:
        user_id = int(user_id)
    except ValueError:
        raise credentials_exception
    
    # 查询用户
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    
    # 检查用户是否激活
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled"
        )
    
    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    获取当前活跃用户（已激活的用户）
    
    Args:
        current_user: 当前用户
        
    Returns:
        当前活跃用户
        
    Raises:
        HTTPException: 用户未激活时抛出
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled"
        )
    return current_user


def get_optional_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    获取可选的当前用户（不强制要求认证）
    
    Args:
        credentials: HTTP认证凭据
        db: 数据库会话
        
    Returns:
        当前用户对象或None
    """
    if not credentials:
        return None
    
    try:
        return get_current_user(credentials, db)
    except HTTPException:
        return None


def get_user_locale(
    current_user: Optional[User] = Depends(get_optional_current_user)
) -> str:
    """
    获取用户语言偏好
    
    Args:
        current_user: 当前用户（可选）
        
    Returns:
        用户语言代码
    """
    if current_user and current_user.preferred_language:
        return current_user.preferred_language
    
    # 如果没有用户或用户没有设置语言偏好，返回默认语言
    from app.core.config import settings
    return settings.DEFAULT_LOCALE


def require_permissions(*permissions: str):
    """
    权限检查装饰器工厂（预留用于未来扩展）
    
    Args:
        permissions: 需要的权限列表
        
    Returns:
        权限检查依赖项
    """
    def permission_checker(
        current_user: User = Depends(get_current_active_user)
    ) -> User:
        # 这里可以实现具体的权限检查逻辑
        # 目前简单返回用户，未来可以扩展角色和权限系统
        return current_user
    
    return permission_checker