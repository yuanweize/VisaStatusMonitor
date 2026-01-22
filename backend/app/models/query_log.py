"""
查询日志模型
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.database import Base


class QueryLog(Base):
    """查询日志模型"""
    
    __tablename__ = "query_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("applications.id"), nullable=False)
    
    # 查询结果
    status = Column(String(50))  # success, error
    application_status = Column(String(100))  # 申请状态
    details = Column(Text)  # 详细信息
    error_message = Column(Text)  # 错误信息（如果有）
    raw_response = Column(Text)  # 原始响应（用于调试）
    
    # 性能信息
    query_timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    response_time_ms = Column(Integer)  # 响应时间（毫秒）
    
    # 关系
    application = relationship("Application", back_populates="query_logs")
    
    def __repr__(self):
        return f"<QueryLog(id={self.id}, application_id={self.application_id}, status='{self.status}')>"
    
    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "application_id": self.application_id,
            "status": self.status,
            "application_status": self.application_status,
            "details": self.details,
            "error_message": self.error_message,
            "query_timestamp": self.query_timestamp.isoformat() if self.query_timestamp else None,
            "response_time_ms": self.response_time_ms
        }