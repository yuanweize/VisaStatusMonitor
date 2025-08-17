"""
申请模型
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.database import Base


class Application(Base):
    """申请模型"""
    
    __tablename__ = "applications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    country_code = Column(String(2), nullable=False, index=True)
    applicant_name = Column(String(100), nullable=False)
    query_code = Column(String(50), nullable=False, index=True)
    query_type = Column(String(50), nullable=False)
    
    # 通知设置（可选，覆盖全局设置）
    notification_method = Column(String(20))  # email, telegram, web, none
    notification_target = Column(String(255))  # 邮箱地址或Telegram ID
    query_interval = Column(String(10))  # 查询间隔：30m, 1h, 2h, 6h, 12h, 1d, 1w
    
    # 状态信息
    latest_status = Column(String(100))  # 最新状态
    latest_details = Column(Text)  # 最新详情
    last_checked = Column(DateTime)  # 最后检查时间
    last_status_change = Column(DateTime)  # 最后状态变化时间
    
    # 系统字段
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    user = relationship("User", back_populates="applications")
    query_logs = relationship("QueryLog", back_populates="application", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="application", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Application(id={self.id}, applicant_name='{self.applicant_name}', country_code='{self.country_code}')>"
    
    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "country_code": self.country_code,
            "applicant_name": self.applicant_name,
            "query_code": self.query_code,
            "query_type": self.query_type,
            "notification_method": self.notification_method,
            "notification_target": self.notification_target,
            "query_interval": self.query_interval,
            "latest_status": self.latest_status,
            "latest_details": self.latest_details,
            "last_checked": self.last_checked.isoformat() if self.last_checked else None,
            "last_status_change": self.last_status_change.isoformat() if self.last_status_change else None,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }