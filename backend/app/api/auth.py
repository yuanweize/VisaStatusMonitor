"""
认证API路由
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_active_user, get_user_locale
from app.core.i18n import get_i18n_manager
from app.schemas.user import UserCreate, UserLogin, UserResponse, TokenResponse
from app.schemas.common import ResponseModel
from app.services.auth_service import AuthService
from app.services.user_service import UserService
from app.models.user import User
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

router = APIRouter()


@router.post("/register", response_model=ResponseModel)
async def register(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    locale: str = Depends(get_user_locale),
    i18n = Depends(get_i18n_manager)
):
    """用户注册"""
    try:
        user_service = UserService(db)
        user = user_service.create_user(user_data)
        
        return ResponseModel(
            success=True,
            message=i18n.get_text("auth.registerSuccess", locale),
            data={"user_id": user.id, "username": user.username}
        )
        
    except Exception as e:
        logger.error(f"Registration failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=i18n.get_text("auth.registerFailed", locale)
        )


@router.post("/login", response_model=TokenResponse)
async def login(
    login_data: UserLogin,
    db: Session = Depends(get_db),
    locale: str = Depends(get_user_locale),
    i18n = Depends(get_i18n_manager)
):
    """用户登录"""
    try:
        auth_service = AuthService(db)
        token_response = auth_service.login(login_data)
        
        return token_response
        
    except Exception as e:
        logger.error(f"Login failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=i18n.get_text("auth.loginFailed", locale),
            headers={"WWW-Authenticate": "Bearer"}
        )


@router.post("/logout", response_model=ResponseModel)
async def logout(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    locale: str = Depends(get_user_locale),
    i18n = Depends(get_i18n_manager)
):
    """用户登出"""
    try:
        auth_service = AuthService(db)
        auth_service.logout(current_user)
        
        return ResponseModel(
            success=True,
            message=i18n.get_text("auth.logoutSuccess", locale)
        )
        
    except Exception as e:
        logger.error(f"Logout failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=i18n.get_text("common.internalError", locale)
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """获取当前用户信息"""
    return current_user


@router.post("/refresh", response_model=TokenResponse)
async def refresh_access_token(
    refresh_token: str,
    db: Session = Depends(get_db),
    locale: str = Depends(get_user_locale),
    i18n = Depends(get_i18n_manager)
):
    """刷新访问令牌"""
    try:
        auth_service = AuthService(db)
        token_response = auth_service.refresh_token(refresh_token)
        
        return token_response
        
    except Exception as e:
        logger.error(f"Token refresh failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=i18n.get_text("auth.tokenInvalid", locale),
            headers={"WWW-Authenticate": "Bearer"}
        )


@router.post("/change-password", response_model=ResponseModel)
async def change_password(
    old_password: str,
    new_password: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    locale: str = Depends(get_user_locale),
    i18n = Depends(get_i18n_manager)
):
    """修改密码"""
    try:
        auth_service = AuthService(db)
        auth_service.change_password(current_user, old_password, new_password)
        
        return ResponseModel(
            success=True,
            message=i18n.get_text("auth.passwordChanged", locale)
        )
        
    except Exception as e:
        logger.error(f"Password change failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=i18n.get_text("auth.passwordChangeFailed", locale)
        )