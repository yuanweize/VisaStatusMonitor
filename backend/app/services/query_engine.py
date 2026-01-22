"""
查询引擎服务
"""

from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime, timedelta

from app.models.application import Application
from app.models.query_log import QueryLog
from app.models.user import User
from app.plugins.plugin_manager import get_plugin_manager
from app.plugins.base_plugin import QueryResult
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class QueryEngine:
    """查询引擎"""
    
    def __init__(self, db: Session):
        self.db = db
        self.plugin_manager = get_plugin_manager()
    
    def execute_query(self, application: Application) -> QueryResult:
        """
        执行查询
        
        Args:
            application: 申请对象
            
        Returns:
            查询结果
        """
        logger.info(f"Executing query for application {application.id}: {application.query_code}")
        
        try:
            # 使用插件管理器执行查询
            result = self.plugin_manager.query_status(
                application.country_code,
                application.query_code,
                application.query_type
            )
            
            # 记录查询日志
            self._log_query_result(application, result)
            
            # 更新申请状态
            if result.status == 'success':
                self._update_application_status(application, result)
            
            return result
            
        except Exception as e:
            logger.error(f"Query execution failed for application {application.id}: {e}")
            
            # 创建错误结果
            error_result = QueryResult(
                status='error',
                error=str(e)
            )
            
            # 记录错误日志
            self._log_query_result(application, error_result)
            
            return error_result    

    def _log_query_result(self, application: Application, result: QueryResult):
        """
        记录查询结果到数据库
        
        Args:
            application: 申请对象
            result: 查询结果
        """
        try:
            query_log = QueryLog(
                application_id=application.id,
                status=result.status,
                application_status=result.application_status,
                details=result.details,
                error_message=result.error,
                raw_response=result.raw_response,
                response_time_ms=result.response_time_ms,
                query_timestamp=result.query_timestamp
            )
            
            self.db.add(query_log)
            self.db.commit()
            
            logger.debug(f"Query log saved for application {application.id}")
            
        except Exception as e:
            logger.error(f"Failed to save query log for application {application.id}: {e}")
            self.db.rollback()
    
    def _update_application_status(self, application: Application, result: QueryResult):
        """
        更新申请状态
        
        Args:
            application: 申请对象
            result: 查询结果
        """
        try:
            # 检查状态是否发生变化
            status_changed = (
                application.latest_status != result.application_status
            )
            
            # 更新申请信息
            application.latest_status = result.application_status
            application.latest_details = result.details
            application.last_checked = result.query_timestamp
            
            if status_changed:
                application.last_status_change = result.query_timestamp
                logger.info(
                    f"Status changed for application {application.id}: "
                    f"{application.latest_status} -> {result.application_status}"
                )
            
            self.db.commit()
            
            # 如果状态发生变化，触发通知
            if status_changed:
                self._trigger_status_change_notification(application, result)
            
        except Exception as e:
            logger.error(f"Failed to update application status for {application.id}: {e}")
            self.db.rollback()
    
    def _trigger_status_change_notification(self, application: Application, result: QueryResult):
        """
        触发状态变化通知
        
        Args:
            application: 申请对象
            result: 查询结果
        """
        try:
            # 这里将集成通知系统
            # TODO: 实现通知发送逻辑
            logger.info(f"Status change notification triggered for application {application.id}")
            
        except Exception as e:
            logger.error(f"Failed to trigger notification for application {application.id}: {e}")
    
    def validate_query_parameters(self, country_code: str, query_code: str, query_type: str) -> bool:
        """
        验证查询参数
        
        Args:
            country_code: 国家代码
            query_code: 查询代码
            query_type: 查询类型
            
        Returns:
            验证结果
        """
        # 检查是否支持该国家
        if not self.plugin_manager.is_country_supported(country_code):
            logger.warning(f"Unsupported country: {country_code}")
            return False
        
        # 检查查询类型是否支持
        supported_types = self.plugin_manager.get_query_types(country_code)
        if query_type not in supported_types:
            logger.warning(f"Unsupported query type {query_type} for country {country_code}")
            return False
        
        # 验证查询代码格式
        if not self.plugin_manager.validate_query_code(country_code, query_code, query_type):
            logger.warning(f"Invalid query code format: {query_code}")
            return False
        
        return True
    
    def get_supported_countries(self) -> List[Dict[str, Any]]:
        """
        获取支持的国家列表
        
        Returns:
            国家信息列表
        """
        countries = []
        
        for country_code in self.plugin_manager.get_supported_countries():
            plugin_info = self.plugin_manager.get_plugin_info(country_code)
            if plugin_info:
                countries.append({
                    'code': country_code,
                    'name': plugin_info.get('country_name', country_code),
                    'query_types': plugin_info.get('supported_query_types', []),
                    'description': plugin_info.get('description', ''),
                    'website': plugin_info.get('website', ''),
                    'available': True
                })
        
        return sorted(countries, key=lambda x: x['name'])
    
    def get_query_statistics(self) -> Dict[str, Any]:
        """
        获取查询统计信息
        
        Returns:
            统计信息
        """
        try:
            # 基本统计
            total_applications = self.db.query(Application).count()
            total_users = self.db.query(User).count()
            total_queries = self.db.query(QueryLog).count()
            
            # 最近24小时的查询数
            yesterday = datetime.utcnow() - timedelta(days=1)
            recent_queries = self.db.query(QueryLog).filter(
                QueryLog.query_timestamp >= yesterday
            ).count()
            
            # 成功查询率
            successful_queries = self.db.query(QueryLog).filter(
                QueryLog.status == 'success'
            ).count()
            success_rate = (successful_queries / total_queries * 100) if total_queries > 0 else 0
            
            # 按国家统计申请数量
            country_stats = self.db.query(
                Application.country_code,
                func.count(Application.id).label('count')
            ).group_by(Application.country_code).all()
            
            country_distribution = [
                {'country': stat.country_code, 'count': stat.count}
                for stat in country_stats
            ]
            
            # 按状态统计申请数量
            status_stats = self.db.query(
                Application.latest_status,
                func.count(Application.id).label('count')
            ).group_by(Application.latest_status).all()
            
            status_distribution = [
                {'status': stat.latest_status or 'unknown', 'count': stat.count}
                for stat in status_stats
            ]
            
            # 最近的查询活动
            recent_activity = self.db.query(QueryLog).order_by(
                desc(QueryLog.query_timestamp)
            ).limit(10).all()
            
            recent_queries_list = [
                {
                    'id': log.id,
                    'application_id': log.application_id,
                    'status': log.status,
                    'timestamp': log.query_timestamp.isoformat() if log.query_timestamp else None,
                    'response_time': log.response_time_ms
                }
                for log in recent_activity
            ]
            
            # 错误统计
            error_queries = self.db.query(QueryLog).filter(
                QueryLog.status == 'error'
            ).count()
            error_rate = (error_queries / total_queries * 100) if total_queries > 0 else 0
            
            return {
                'overview': {
                    'total_applications': total_applications,
                    'total_users': total_users,
                    'total_queries': total_queries,
                    'recent_queries_24h': recent_queries,
                    'success_rate': round(success_rate, 2),
                    'error_rate': round(error_rate, 2)
                },
                'distributions': {
                    'by_country': country_distribution,
                    'by_status': status_distribution
                },
                'recent_activity': recent_queries_list,
                'plugin_stats': self.plugin_manager.get_plugin_stats()
            }
            
        except Exception as e:
            logger.error(f"Failed to get query statistics: {e}")
            return {
                'overview': {
                    'total_applications': 0,
                    'total_users': 0,
                    'total_queries': 0,
                    'recent_queries_24h': 0,
                    'success_rate': 0,
                    'error_rate': 0
                },
                'distributions': {
                    'by_country': [],
                    'by_status': []
                },
                'recent_activity': [],
                'plugin_stats': {}
            }
    
    def get_application_statistics(self, user_id: Optional[int] = None) -> Dict[str, Any]:
        """
        获取申请统计信息（可按用户过滤）
        
        Args:
            user_id: 用户ID（可选）
            
        Returns:
            申请统计信息
        """
        try:
            query = self.db.query(Application)
            if user_id:
                query = query.filter(Application.user_id == user_id)
            
            applications = query.all()
            
            if not applications:
                return {
                    'total': 0,
                    'by_status': {},
                    'by_country': {},
                    'recent_changes': []
                }
            
            # 按状态统计
            status_counts = {}
            for app in applications:
                status = app.latest_status or 'unknown'
                status_counts[status] = status_counts.get(status, 0) + 1
            
            # 按国家统计
            country_counts = {}
            for app in applications:
                country = app.country_code
                country_counts[country] = country_counts.get(country, 0) + 1
            
            # 最近状态变化
            recent_changes = sorted(
                [app for app in applications if app.last_status_change],
                key=lambda x: x.last_status_change,
                reverse=True
            )[:5]
            
            recent_changes_list = [
                {
                    'id': app.id,
                    'name': app.name,
                    'country': app.country_code,
                    'status': app.latest_status,
                    'changed_at': app.last_status_change.isoformat() if app.last_status_change else None
                }
                for app in recent_changes
            ]
            
            return {
                'total': len(applications),
                'by_status': status_counts,
                'by_country': country_counts,
                'recent_changes': recent_changes_list
            }
            
        except Exception as e:
            logger.error(f"Failed to get application statistics: {e}")
            return {
                'total': 0,
                'by_status': {},
                'by_country': {},
                'recent_changes': []
            }