"""
数据库迁移工具
"""

from sqlalchemy import text
from app.core.database import engine, SessionLocal
from app.models import User, Application, QueryLog, Notification
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


def create_initial_data():
    """创建初始数据"""
    db = SessionLocal()
    try:
        # 检查是否已有数据
        user_count = db.query(User).count()
        if user_count > 0:
            logger.info("Database already has data, skipping initial data creation")
            return
        
        logger.info("Creating initial data...")
        
        # 可以在这里添加初始数据创建逻辑
        # 例如：创建默认管理员用户等
        
        db.commit()
        logger.info("Initial data created successfully")
        
    except Exception as e:
        logger.error(f"Failed to create initial data: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def check_and_upgrade_schema():
    """检查并升级数据库模式"""
    try:
        with engine.connect() as connection:
            # 检查表是否存在
            result = connection.execute(text("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name IN ('users', 'applications', 'query_logs', 'notifications')
            """))
            
            existing_tables = [row[0] for row in result]
            expected_tables = ['users', 'applications', 'query_logs', 'notifications']
            
            missing_tables = set(expected_tables) - set(existing_tables)
            
            if missing_tables:
                logger.warning(f"Missing tables: {missing_tables}")
                return False
            
            logger.info("All required tables exist")
            return True
            
    except Exception as e:
        logger.error(f"Schema check failed: {e}")
        return False


def run_migrations():
    """运行数据库迁移"""
    try:
        logger.info("Starting database migrations...")
        
        # 检查模式
        if not check_and_upgrade_schema():
            logger.warning("Schema check failed, but continuing...")
        
        # 创建初始数据
        create_initial_data()
        
        logger.info("Database migrations completed successfully")
        
    except Exception as e:
        logger.error(f"Database migrations failed: {e}")
        raise