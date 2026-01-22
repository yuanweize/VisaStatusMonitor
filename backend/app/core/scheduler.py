"""
后台任务调度器
"""

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.executors.asyncio import AsyncIOExecutor
import asyncio
from typing import Dict, Any

from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class VisaScheduler:
    """签证状态查询调度器"""
    
    def __init__(self):
        # 配置调度器
        jobstores = {
            'default': MemoryJobStore()
        }
        executors = {
            'default': AsyncIOExecutor()
        }
        job_defaults = {
            'coalesce': False,
            'max_instances': 3
        }
        
        self.scheduler = AsyncIOScheduler(
            jobstores=jobstores,
            executors=executors,
            job_defaults=job_defaults,
            timezone='UTC'
        )
        
        self._running = False
    
    def start(self):
        """启动调度器"""
        if not self._running:
            self.scheduler.start()
            self._running = True
            logger.info("Scheduler started")
    
    def shutdown(self):
        """关闭调度器"""
        if self._running:
            self.scheduler.shutdown()
            self._running = False
            logger.info("Scheduler stopped")
    
    @property
    def running(self) -> bool:
        """检查调度器是否运行中"""
        return self._running and self.scheduler.running
    
    def add_query_job(self, application_id: int, interval: str, **kwargs):
        """添加查询任务"""
        job_id = f"query_app_{application_id}"
        
        # 解析时间间隔
        interval_seconds = self._parse_interval(interval)
        
        # 添加任务
        self.scheduler.add_job(
            func=self._execute_query,
            trigger='interval',
            seconds=interval_seconds,
            id=job_id,
            args=[application_id],
            kwargs=kwargs,
            replace_existing=True
        )
        
        logger.info(f"Added query job for application {application_id} with interval {interval}")
    
    def remove_query_job(self, application_id: int):
        """移除查询任务"""
        job_id = f"query_app_{application_id}"
        try:
            self.scheduler.remove_job(job_id)
            logger.info(f"Removed query job for application {application_id}")
        except Exception as e:
            logger.warning(f"Failed to remove job {job_id}: {e}")
    
    def _parse_interval(self, interval: str) -> int:
        """解析时间间隔字符串为秒数"""
        if not interval:
            return 3600  # 默认1小时
        
        unit = interval[-1].lower()
        try:
            value = int(interval[:-1])
        except ValueError:
            logger.warning(f"Invalid interval format: {interval}, using default 1h")
            return 3600
        
        multipliers = {
            'm': 60,      # 分钟
            'h': 3600,    # 小时
            'd': 86400,   # 天
            'w': 604800   # 周
        }
        
        return value * multipliers.get(unit, 3600)
    
    async def _execute_query(self, application_id: int):
        """执行查询任务"""
        try:
            logger.info(f"Executing query for application {application_id}")
            
            # 这里将调用查询引擎执行实际查询
            # 暂时只记录日志
            # TODO: 实现实际的查询逻辑
            
            # 添加随机延迟（1分钟内）
            import random
            delay = random.uniform(0, 60)
            await asyncio.sleep(delay)
            
            logger.info(f"Query completed for application {application_id}")
            
        except Exception as e:
            logger.error(f"Query failed for application {application_id}: {e}")


# 创建全局调度器实例
scheduler = VisaScheduler()