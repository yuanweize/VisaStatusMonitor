"""
VisaStatusMonitor - 主应用入口
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
import traceback
import time

from app.core.config import settings
from app.core.database import create_database_and_tables
from app.core.scheduler import scheduler
from app.core.startup import initialize_application
from app.core.i18n import i18n_manager
from app.utils.logger import setup_logger

# 设置日志
logger = setup_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    logger.info("Starting VisaStatusMonitor...")
    
    # 初始化应用
    initialize_application()
    
    # 初始化国际化
    i18n_manager.load_translations()
    logger.info(f"I18n initialized with locales: {i18n_manager.supported_locales}")
    
    # 创建数据库和表
    create_database_and_tables()
    
    # 启动调度器
    scheduler.start()
    logger.info("Scheduler started")
    
    yield
    
    # 关闭时执行
    logger.info("Shutting down VisaStatusMonitor...")
    scheduler.shutdown()
    logger.info("Scheduler stopped")


# 创建FastAPI应用
app = FastAPI(
    title="VisaStatusMonitor API",
    description="国际化签证状态查询系统API",
    version="1.0.0",
    lifespan=lifespan
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


# 请求处理时间中间件
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    
    # 记录请求日志
    logger.info(
        f"{request.method} {request.url.path} - "
        f"Status: {response.status_code} - "
        f"Time: {process_time:.4f}s"
    )
    return response


# 全局异常处理器
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.warning(f"HTTP {exc.status_code}: {exc.detail} - {request.url}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "message": exc.detail,
            "status_code": exc.status_code,
            "path": str(request.url.path)
        }
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.warning(f"Validation error: {exc.errors()} - {request.url}")
    return JSONResponse(
        status_code=422,
        content={
            "error": True,
            "message": "请求数据验证失败",
            "details": exc.errors(),
            "status_code": 422,
            "path": str(request.url.path)
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)} - {request.url}")
    logger.error(traceback.format_exc())
    
    if settings.DEBUG:
        return JSONResponse(
            status_code=500,
            content={
                "error": True,
                "message": str(exc),
                "traceback": traceback.format_exc(),
                "status_code": 500,
                "path": str(request.url.path)
            }
        )
    else:
        return JSONResponse(
            status_code=500,
            content={
                "error": True,
                "message": "服务器内部错误",
                "status_code": 500,
                "path": str(request.url.path)
            }
        )


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "VisaStatusMonitor API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "scheduler_running": scheduler.running
    }


# 导入路由
from app.api import health, auth, users, system

# 注册路由
app.include_router(health.router, prefix="/api", tags=["系统"])
app.include_router(auth.router, prefix="/api/auth", tags=["认证"])
app.include_router(users.router, prefix="/api/users", tags=["用户"])
app.include_router(system.router, prefix="/api/system", tags=["系统状态"])

# 其他路由（稍后实现）
# from app.api import applications, notifications
# app.include_router(applications.router, prefix="/api/applications", tags=["申请"])
# app.include_router(notifications.router, prefix="/api/notifications", tags=["通知"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )