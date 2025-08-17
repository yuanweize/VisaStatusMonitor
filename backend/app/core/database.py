"""
数据库连接和配置
"""

from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
import os
from pathlib import Path
from typing import Generator

from .config import settings
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

# 数据库连接配置
connect_args = {}
engine_kwargs = {
    "echo": settings.DEBUG  # 在调试模式下显示SQL语句
}

# SQLite特定配置
if "sqlite" in settings.DATABASE_URL:
    connect_args = {
        "check_same_thread": False,
        "timeout": 20  # 连接超时时间
    }
    engine_kwargs.update({
        "poolclass": StaticPool,
        "connect_args": connect_args
    })
else:
    # MySQL/PostgreSQL配置
    engine_kwargs.update({
        "pool_size": 10,
        "max_overflow": 20,
        "pool_pre_ping": True,  # 连接前检查
        "pool_recycle": 3600,   # 连接回收时间
        "connect_args": connect_args
    })

# 创建数据库引擎
engine = create_engine(settings.DATABASE_URL, **engine_kwargs)

# SQLite外键约束支持
if "sqlite" in settings.DATABASE_URL:
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基础模型类
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """获取数据库会话（依赖注入）"""
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def create_database_and_tables():
    """创建数据库和所有表"""
    try:
        # 确保数据目录存在
        if "sqlite" in settings.DATABASE_URL:
            db_path = settings.DATABASE_URL.replace("sqlite:///", "")
            db_dir = os.path.dirname(db_path)
            if db_dir:
                Path(db_dir).mkdir(parents=True, exist_ok=True)
                logger.info(f"Created database directory: {db_dir}")
        
        # 导入所有模型以确保它们被注册
        from app.models import User, Application, QueryLog, Notification
        
        # 创建所有表
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
        
    except Exception as e:
        logger.error(f"Failed to create database tables: {e}")
        raise


def check_database_connection() -> bool:
    """检查数据库连接"""
    try:
        with engine.connect() as connection:
            connection.execute("SELECT 1")
        return True
    except Exception as e:
        logger.error(f"Database connection check failed: {e}")
        return False


def get_database_info() -> dict:
    """获取数据库信息"""
    try:
        db_type = settings.DATABASE_URL.split("://")[0]
        
        info = {
            "type": db_type,
            "url_masked": f"{db_type}://***",
            "connected": check_database_connection()
        }
        
        if "sqlite" in settings.DATABASE_URL:
            db_path = settings.DATABASE_URL.replace("sqlite:///", "")
            info.update({
                "file_path": db_path,
                "file_exists": os.path.exists(db_path),
                "file_size": os.path.getsize(db_path) if os.path.exists(db_path) else 0
            })
        
        return info
    except Exception as e:
        logger.error(f"Failed to get database info: {e}")
        return {"error": str(e)}


# 创建数据库会话的便捷函数
def create_session() -> Session:
    """创建新的数据库会话"""
    return SessionLocal()