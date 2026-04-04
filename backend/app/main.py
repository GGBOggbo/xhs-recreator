"""
FastAPI 应用入口
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from loguru import logger

from app.config import settings
from app.api.routes import router as api_router
from app.api.auth import router as auth_router
from app.api.websocket import router as ws_router

# 确保目录在模块加载时就存在（静态文件挂载需要）
settings.output_dir.mkdir(parents=True, exist_ok=True)
settings.data_dir.mkdir(parents=True, exist_ok=True)
(settings.output_dir / "images").mkdir(exist_ok=True)
(settings.output_dir / "texts").mkdir(exist_ok=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时
    logger.info("Starting XHS ReCreator...")
    logger.info(f"Output directory: {settings.output_dir}")
    logger.info(f"Data directory: {settings.data_dir}")

    yield

    # 关闭时
    logger.info("Shutting down XHS ReCreator...")


app = FastAPI(
    title="XHS ReCreator",
    description="小红书内容二创工具 API",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应限制
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 静态文件服务 - 生成的图片
app.mount("/output", StaticFiles(directory=str(settings.output_dir)), name="output")

# 注册路由
app.include_router(auth_router, prefix="/api")
app.include_router(api_router, prefix="/api")
app.include_router(ws_router, prefix="/ws")


@app.get("/")
async def root():
    """健康检查"""
    return {"status": "ok", "message": "XHS ReCreator API is running"}


@app.get("/health")
async def health():
    """健康检查端点"""
    return {"status": "healthy"}
