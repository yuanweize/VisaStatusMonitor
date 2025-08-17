"""
通知记录模型
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.database import Base


class Notification(Base):
    """通知记录模型"""
    
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("applications.id"), nullable=False)
    
    # 通知信息
    notification_type = Column(String(20), nullable=False)  # email, telegram, web
    recipient = Column(String(255), nullable=False)  # 接收者（邮箱或Telegram ID）
    subject = Column(String(255))  # 主题（邮件用）
    message = Column(Text, nullable=False)  # 消息内容
    
    # 状态信息
    status = Column(String(20), default='pending')  # pending, sent, failed
    sent_at = Column(DateTime)  # 发送时间
    error_message = Column(Text)  # 错误信息（如果发送失败）
    retry_count = Column(Integer, default=0)  # 重试次数
    
    # 系统字段
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    application = relationship("Application", back_populates="notifications")
    
    def __repr__(self):
        return f"<Notification(id={self.id}, type='{self.notification_type}', status='{self.status}')>"
    
    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "application_id": self.application_id,
            "notification_type": self.notification_type,
            "recipient": self.recipient,
            "subject": self.subject,
            "message": self.message,
            "status": self.status,
            "sent_at": self.sent_at.isoformat() if self.sent_at else None,
            "error_message": self.error_message,
            "retry_count": self.retry_count,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }