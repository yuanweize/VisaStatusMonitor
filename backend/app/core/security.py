"""
安全相关工具
"""

from datetime import datetime, timedelta
from typing import Optional, Union
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status

from app.core.config import settings
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    创建JWT访问令牌
    
    Args:
        data: 要编码的数据
        expires_delta: 过期时间增量
        
    Returns:
        JWT令牌字符串
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    
    try:
        encoded_jwt = jwt.encode(
            to_encode, 
            settings.SECRET_KEY, 
            algorithm=settings.JWT_ALGORITHM
        )
        return encoded_jwt
    except Exception as e:
        logger.error(f"Failed to create access token: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not create access token"
        )


def verify_token(token: str) -> Optional[dict]:
    """
    验证JWT令牌
    
    Args:
        token: JWT令牌字符串
        
    Returns:
        解码后的数据，如果验证失败返回None
    """
    try:
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except JWTError as e:
        logger.warning(f"JWT verification failed: {e}")
        return None
    except Exception as e:
        logger.error(f"Token verification error: {e}")
        return None


def get_password_hash(password: str) -> str:
    """
    生成密码哈希
    
    Args:
        password: 明文密码
        
    Returns:
        密码哈希
    """
    try:
        return pwd_context.hash(password)
    except Exception as e:
        logger.error(f"Failed to hash password: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not hash password"
        )


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    验证密码
    
    Args:
        plain_password: 明文密码
        hashed_password: 哈希密码
        
    Returns:
        验证结果
    """
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        logger.error(f"Password verification error: {e}")
        return False


def generate_password_reset_token(email: str) -> str:
    """
    生成密码重置令牌
    
    Args:
        email: 用户邮箱
        
    Returns:
        重置令牌
    """
    delta = timedelta(hours=1)  # 重置令牌1小时有效
    return create_access_token(
        data={"sub": email, "type": "password_reset"}, 
        expires_delta=delta
    )


def verify_password_reset_token(token: str) -> Optional[str]:
    """
    验证密码重置令牌
    
    Args:
        token: 重置令牌
        
    Returns:
        用户邮箱，如果验证失败返回None
    """
    payload = verify_token(token)
    if payload and payload.get("type") == "password_reset":
        return payload.get("sub")
    return None


def create_refresh_token(user_id: int) -> str:
    """
    创建刷新令牌
    
    Args:
        user_id: 用户ID
        
    Returns:
        刷新令牌
    """
    delta = timedelta(days=7)  # 刷新令牌7天有效
    return create_access_token(
        data={"sub": str(user_id), "type": "refresh"}, 
        expires_delta=delta
    )


def verify_refresh_token(token: str) -> Optional[int]:
    """
    验证刷新令牌
    
    Args:
        token: 刷新令牌
        
    Returns:
        用户ID，如果验证失败返回None
    """
    payload = verify_token(token)
    if payload and payload.get("type") == "refresh":
        try:
            return int(payload.get("sub"))
        except (ValueError, TypeError):
            return None
    return None