"""
用户服务
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash
from app.core.exceptions import ConflictException, NotFoundException
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class UserService:
    """用户服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_user(self, user_data: UserCreate) -> User:
        """
        创建新用户
        
        Args:
            user_data: 用户创建数据
            
        Returns:
            创建的用户对象
            
        Raises:
            ConflictException: 用户名或邮箱已存在
        """
        try:
            # 检查用户名是否已存在
            existing_user = self.db.query(User).filter(
                User.username == user_data.username
            ).first()
            if existing_user:
                raise ConflictException("Username already exists")
            
            # 检查邮箱是否已存在
            existing_email = self.db.query(User).filter(
                User.email == user_data.email
            ).first()
            if existing_email:
                raise ConflictException("Email already exists")
            
            # 创建用户
            hashed_password = get_password_hash(user_data.password)
            
            db_user = User(
                username=user_data.username,
                email=user_data.email,
                password_hash=hashed_password,
                preferred_language=user_data.preferred_language,
                timezone=user_data.timezone
            )
            
            self.db.add(db_user)
            self.db.commit()
            self.db.refresh(db_user)
            
            logger.info(f"User created: {db_user.username} (ID: {db_user.id})")
            return db_user
            
        except IntegrityError as e:
            self.db.rollback()
            logger.error(f"Database integrity error creating user: {e}")
            raise ConflictException("User with this username or email already exists")
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating user: {e}")
            raise
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """
        根据ID获取用户
        
        Args:
            user_id: 用户ID
            
        Returns:
            用户对象或None
        """
        return self.db.query(User).filter(User.id == user_id).first()
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """
        根据用户名获取用户
        
        Args:
            username: 用户名
            
        Returns:
            用户对象或None
        """
        return self.db.query(User).filter(User.username == username).first()
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """
        根据邮箱获取用户
        
        Args:
            email: 邮箱地址
            
        Returns:
            用户对象或None
        """
        return self.db.query(User).filter(User.email == email).first()
    
    def update_user(self, user_id: int, user_data: UserUpdate) -> User:
        """
        更新用户信息
        
        Args:
            user_id: 用户ID
            user_data: 更新数据
            
        Returns:
            更新后的用户对象
            
        Raises:
            NotFoundException: 用户不存在
            ConflictException: 邮箱已被其他用户使用
        """
        user = self.get_user_by_id(user_id)
        if not user:
            raise NotFoundException("User not found")
        
        try:
            # 检查邮箱是否被其他用户使用
            if user_data.email and user_data.email != user.email:
                existing_email = self.db.query(User).filter(
                    User.email == user_data.email,
                    User.id != user_id
                ).first()
                if existing_email:
                    raise ConflictException("Email already exists")
            
            # 更新用户信息
            update_data = user_data.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(user, field, value)
            
            self.db.commit()
            self.db.refresh(user)
            
            logger.info(f"User updated: {user.username} (ID: {user.id})")
            return user
            
        except IntegrityError as e:
            self.db.rollback()
            logger.error(f"Database integrity error updating user: {e}")
            raise ConflictException("Email already exists")
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating user: {e}")
            raise
    
    def delete_user(self, user_id: int) -> bool:
        """
        删除用户（软删除）
        
        Args:
            user_id: 用户ID
            
        Returns:
            删除是否成功
            
        Raises:
            NotFoundException: 用户不存在
        """
        user = self.get_user_by_id(user_id)
        if not user:
            raise NotFoundException("User not found")
        
        try:
            # 软删除：设置为非活跃状态
            user.is_active = False
            self.db.commit()
            
            logger.info(f"User deactivated: {user.username} (ID: {user.id})")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deactivating user: {e}")
            raise
    
    def activate_user(self, user_id: int) -> User:
        """
        激活用户
        
        Args:
            user_id: 用户ID
            
        Returns:
            激活后的用户对象
            
        Raises:
            NotFoundException: 用户不存在
        """
        user = self.get_user_by_id(user_id)
        if not user:
            raise NotFoundException("User not found")
        
        try:
            user.is_active = True
            self.db.commit()
            self.db.refresh(user)
            
            logger.info(f"User activated: {user.username} (ID: {user.id})")
            return user
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error activating user: {e}")
            raise
    
    def get_users(self, skip: int = 0, limit: int = 100, active_only: bool = True) -> List[User]:
        """
        获取用户列表
        
        Args:
            skip: 跳过的记录数
            limit: 限制返回的记录数
            active_only: 是否只返回活跃用户
            
        Returns:
            用户列表
        """
        query = self.db.query(User)
        
        if active_only:
            query = query.filter(User.is_active == True)
        
        return query.offset(skip).limit(limit).all()
    
    def count_users(self, active_only: bool = True) -> int:
        """
        统计用户数量
        
        Args:
            active_only: 是否只统计活跃用户
            
        Returns:
            用户数量
        """
        query = self.db.query(User)
        
        if active_only:
            query = query.filter(User.is_active == True)
        
        return query.count()