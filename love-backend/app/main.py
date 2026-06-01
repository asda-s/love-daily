"""
FastAPI应用入口模块
负责创建FastAPI实例、配置跨域、挂载路由、统一异常处理
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from loguru import logger
from app.database import engine, Base
from app.routers import user, memory, life, interact, love
from app.routers import websocket
from app.tasks import init_scheduler, shutdown_scheduler
from app.response import success_response, error_response
from app.exceptions import AppException
import os
import sys

# 配置loguru日志
logger.remove()
logger.add(sys.stdout, level="INFO", format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}")
log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
os.makedirs(log_dir, exist_ok=True)
logger.add(
    os.path.join(log_dir, "app_{time:YYYY-MM-DD}.log"),
    rotation="00:00",
    retention="30 days",
    level="DEBUG",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {module}:{function}:{line} | {message}"
)

Base.metadata.create_all(bind=engine)

# 简单迁移：添加 bind_time 列（如不存在）
try:
    with engine.connect() as conn:
        from sqlalchemy import text
        db_type = engine.url.drivername
        if 'postgresql' in db_type:
            conn.execute(text("DO $$ BEGIN ALTER TABLE users ADD COLUMN bind_time TIMESTAMP DEFAULT NULL; EXCEPTION WHEN duplicate_column THEN NULL; END $$"))
        else:
            conn.execute(text("ALTER TABLE users ADD COLUMN bind_time DATETIME DEFAULT NULL"))
        conn.commit()
        logger.info("迁移: 添加 bind_time 列")
except Exception as e:
    logger.warning(f"迁移跳过（列可能已存在）: {str(e)}")

# 简单迁移：mood_diaries 表新增列
try:
    with engine.connect() as conn:
        from sqlalchemy import text
        db_type = engine.url.drivername
        if 'postgresql' in db_type:
            conn.execute(text("DO $$ BEGIN ALTER TABLE mood_diaries ADD COLUMN diary_date DATE NOT NULL DEFAULT CURRENT_DATE; EXCEPTION WHEN duplicate_column THEN NULL; END $$"))
            conn.execute(text("DO $$ BEGIN ALTER TABLE mood_diaries ADD COLUMN second_mood VARCHAR(20); EXCEPTION WHEN duplicate_column THEN NULL; END $$"))
            conn.execute(text("DO $$ BEGIN ALTER TABLE mood_diaries ADD COLUMN mood_intensity INTEGER DEFAULT 3; EXCEPTION WHEN duplicate_column THEN NULL; END $$"))
            conn.execute(text("DO $$ BEGIN ALTER TABLE mood_diaries ADD COLUMN images TEXT; EXCEPTION WHEN duplicate_column THEN NULL; END $$"))
            conn.execute(text("DO $$ BEGIN ALTER TABLE mood_diaries ADD COLUMN tags TEXT; EXCEPTION WHEN duplicate_column THEN NULL; END $$"))
            conn.execute(text("DO $$ BEGIN ALTER TABLE mood_diaries ADD COLUMN is_read BOOLEAN DEFAULT FALSE; EXCEPTION WHEN duplicate_column THEN NULL; END $$"))
            conn.execute(text("DO $$ BEGIN ALTER TABLE mood_diaries ADD COLUMN read_time TIMESTAMP; EXCEPTION WHEN duplicate_column THEN NULL; END $$"))
            conn.execute(text("DO $$ BEGIN ALTER TABLE mood_diaries ADD COLUMN publish_status VARCHAR(20) DEFAULT 'published'; EXCEPTION WHEN duplicate_column THEN NULL; END $$"))
            conn.execute(text("DO $$ BEGIN ALTER TABLE mood_diaries ADD COLUMN scheduled_time TIMESTAMP; EXCEPTION WHEN duplicate_column THEN NULL; END $$"))
        conn.commit()
        logger.info("迁移: mood_diaries 表新增列检查完成")
except Exception as e:
    logger.warning(f"迁移跳过（列可能已存在）: {str(e)}")

# 简单迁移：扩展图片列为TEXT（支持base64存储）
try:
    with engine.connect() as conn:
        from sqlalchemy import text
        db_type = engine.url.drivername
        if 'postgresql' in db_type:
            conn.execute(text("ALTER TABLE users ALTER COLUMN avatar TYPE TEXT"))
            conn.execute(text("ALTER TABLE wishes ALTER COLUMN image TYPE TEXT"))
            conn.execute(text("ALTER TABLE checkin_records ALTER COLUMN image TYPE TEXT"))
        conn.commit()
        logger.info("迁移: 图片列扩展为TEXT完成")
except Exception as e:
    logger.warning(f"迁移跳过: {str(e)}")

# 限流器
limiter = Limiter(key_func=get_remote_address, default_limits=["200/minute"])

app = FastAPI(
    title="心动日常 - 情侣专属系统",
    description="为情侣打造专属的私密互动系统API",
    version="1.0.0"
)
app.state.limiter = limiter

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载上传文件目录为静态资源
upload_dir = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(upload_dir, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=upload_dir), name="uploads")


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content=error_response(429, "请求过于频繁，请稍后再试")
    )


@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.code,
        content=error_response(exc.code, exc.message)
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error("服务器内部错误: {}", str(exc), exc_info=True)
    return JSONResponse(
        status_code=500,
        content=error_response(500, "服务器内部错误，请稍后重试")
    )


@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return JSONResponse(
        status_code=404,
        content=error_response(404, "请求的资源不存在")
    )


@app.exception_handler(422)
async def validation_error_handler(request: Request, exc):
    return JSONResponse(
        status_code=422,
        content=error_response(422, "参数校验失败")
    )


@app.middleware("http")
async def log_requests(request: Request, call_next):
    client_host = request.client.host if request.client else "unknown"
    logger.info(f"{request.method} {request.url.path} from {client_host}")
    response = await call_next(request)
    if response.status_code >= 400:
        logger.warning(f"{request.method} {request.url.path} -> {response.status_code}")
    return response


app.include_router(user.router, prefix="/user", tags=["用户模块"])
app.include_router(memory.router, prefix="/memory", tags=["时光档案馆模块"])
app.include_router(life.router, prefix="/life", tags=["生活管家模块"])
app.include_router(interact.router, prefix="/interact", tags=["双人互动模块"])
app.include_router(love.router, prefix="/love", tags=["恋爱养成模块"])
app.include_router(websocket.router, prefix="/ws", tags=["WebSocket"])


@app.get("/")
async def root():
    return success_response(message="心动日常API服务运行中")


@app.get("/health")
async def health_check():
    return success_response(data={"status": "healthy"}, message="服务正常")


@app.on_event("startup")
async def startup_event():
    from app.security import SECRET_KEY
    if SECRET_KEY == "your-secret-key-change-this-in-production":
        logger.warning("⚠️ 使用默认SECRET_KEY，请在.env中配置自定义密钥！")
    init_scheduler()
    logger.info("心动日常服务启动完成")


@app.on_event("shutdown")
async def shutdown_event():
    shutdown_scheduler()
    logger.info("心动日常服务已关闭")
