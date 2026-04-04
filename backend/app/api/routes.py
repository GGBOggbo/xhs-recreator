"""
API 路由定义
"""
import asyncio
import uuid
from typing import Optional
from pathlib import Path

from fastapi import APIRouter, HTTPException, Query, BackgroundTasks, Depends
from loguru import logger
from sqlalchemy import desc

from app.config import settings
from app.models.task import (
    CreateTaskRequest,
    TaskResponse,
    TaskStatus,
    TaskResult,
    HistoryResponse,
    HistoryItem,
    Task,
    Base,
    sessionmaker,
    create_engine,
)
from app.services.task_runner import task_runner
from app.middleware.auth import get_current_user
from app.models.user import User
from app.utils.crypto import decrypt_cookie

router = APIRouter()

# 数据库连接 - 使用配置中的 database_url
# 确保数据目录存在
import os
db_path = Path(settings.database_url.replace("sqlite:///", ""))
db_path.parent.mkdir(parents=True, exist_ok=True)

engine = create_engine(settings.database_url, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建表
Base.metadata.create_all(bind=engine)


def _get_user_cookie(user_id: int, db) -> str | None:
    """从数据库读取用户的加密 Cookie，解密后返回明文"""
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user or not db_user.xhs_cookies_encrypted:
        return None
    return decrypt_cookie(db_user.xhs_cookies_encrypted)


@router.get("/fetch")
async def fetch_note(url: str, user: dict = Depends(get_current_user)):
    """
    只爬取笔记内容，不执行二创

    - 获取标题、文案、标签、图片
    - 返回原始内容供前端预览
    """
    import urllib.parse

    from app.services.spider import spider_service
    from app.domain.interfaces import CrawlerProvider

    # 读取用户 Cookie
    db = SessionLocal()
    try:
        cookies_plain = _get_user_cookie(user["user_id"], db)
    finally:
        db.close()

    if not cookies_plain:
        raise HTTPException(status_code=400, detail="请先在小红书 Cookie 设置中配置您的 Cookie")

    crawler: CrawlerProvider = spider_service
    success, msg, note_content = crawler.fetch_note(url, cookies=cookies_plain)

    if not success:
        raise HTTPException(status_code=400, detail=msg)

    # 图片URL转为代理URL，绕过防盗链
    proxy_images = []
    for img_url in note_content.images:
        encoded_url = urllib.parse.quote(img_url, safe='')
        proxy_images.append(f"/api/proxy-image?url={encoded_url}")

    return {
        "success": True,
        "data": {
            "note_id": note_content.note_id,
            "title": note_content.title,
            "description": note_content.description,
            "tags": note_content.tags,
            "images": proxy_images,
            "original_images": note_content.images,  # 保留原始URL
            "author_name": note_content.author_name,
            "author_id": note_content.author_id,
            "like_count": note_content.like_count,
            "collect_count": note_content.collect_count,
            "comment_count": note_content.comment_count,
            "share_count": note_content.share_count,
            "note_type": note_content.note_type,
        }
    }


@router.get("/proxy-image")
async def proxy_image(url: str, user: dict = Depends(get_current_user)):
    """
    代理图片请求，绕过防盗链

    小红书图片需要正确的 Referer 才能访问
    """
    import httpx
    from fastapi.responses import Response

    headers = {
        "Referer": "https://www.xiaohongshu.com/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    async with httpx.AsyncClient(timeout=30) as client:
        try:
            response = await client.get(url, headers=headers, follow_redirects=True)
            return Response(
                content=response.content,
                media_type=response.headers.get("content-type", "image/jpeg"),
                headers={
                    "Cache-Control": "public, max-age=86400",
                    "Access-Control-Allow-Origin": "*",
                }
            )
        except Exception as e:
            logger.error(f"代理图片失败: {e}")
            raise HTTPException(status_code=400, detail=f"获取图片失败: {str(e)}")


def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/image-styles")
async def get_image_styles(user: dict = Depends(get_current_user)):
    """获取可选的图片风格列表"""
    from app.config import prompt_config
    return {
        "styles": prompt_config.image_styles_list,
        "default": "notebook"
    }


def run_task_background(task_id: str, image_count: int, selected_indices: list[int], user_prompt: str, image_model: str, image_ratio: str, vision_model: str, image_style_id: str, cookies_plain: str):
    """后台运行任务"""
    import asyncio

    db = SessionLocal()
    try:
        task = db.query(Task).filter(Task.task_id == task_id).first()
        if task:
            # 创建新的事件循环
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(
                    task_runner.run_task(task, db, image_count, selected_indices, user_prompt, image_model, image_ratio, vision_model, image_style_id, cookies_plain=cookies_plain)
                )
            finally:
                loop.close()
    finally:
        db.close()


@router.post("/task", response_model=TaskResponse)
async def create_task(
    request: CreateTaskRequest,
    background_tasks: BackgroundTasks,
    user: dict = Depends(get_current_user),
):
    """
    创建新任务

    - 验证链接
    - 创建任务记录
    - 启动后台处理
    - 返回任务 ID
    """
    task_id = str(uuid.uuid4())

    # 读取用户 Cookie
    db = SessionLocal()
    try:
        cookies_plain = _get_user_cookie(user["user_id"], db)
        if not cookies_plain:
            raise HTTPException(status_code=400, detail="请先在小红书 Cookie 设置中配置您的 Cookie")

        # 创建数据库记录
        task = Task(
            task_id=task_id,
            url=request.url,
            status=TaskStatus.PENDING.value,
            image_count=request.image_count,
            user_prompt=request.user_prompt,
            image_model=request.image_model,
            vision_model=request.vision_model,
            image_style_id=request.image_style_id,
            user_id=user["user_id"],
        )
        db.add(task)
        db.commit()
    finally:
        db.close()

    # 启动后台任务（传 Cookie 明文，避免后台线程中再查库）
    background_tasks.add_task(
        run_task_background,
        task_id,
        request.image_count,
        request.selected_indices or list(range(request.image_count)),
        request.user_prompt or "",
        request.image_model or "nano-banana-2",
        request.image_ratio or "3:4",
        request.vision_model or "glm-4.6v-flash",
        request.image_style_id or "notebook",
        cookies_plain,
    )

    logger.info(f"Created task: {task_id}")

    return TaskResponse(
        task_id=task_id,
        status=TaskStatus.PENDING,
        message="任务已创建，正在处理中"
    )


@router.get("/task/{task_id}")
async def get_task(task_id: str, user: dict = Depends(get_current_user)):
    """获取任务详情"""
    db = SessionLocal()
    try:
        task = db.query(Task).filter(Task.task_id == task_id, Task.user_id == user["user_id"]).first()
        if not task:
            raise HTTPException(status_code=404, detail="任务不存在")

        # 处理生成图片的 URL
        generated_image_urls = []
        if task.generated_images:
            for path in task.generated_images:
                # 转换本地路径为 URL
                # 路径格式可能是: /output/images/{task_id}/generated_0.png
                if path.startswith("/output/"):
                    url_path = path  # 已经是正确的 URL 格式
                elif path.startswith("/app/output/"):
                    url_path = path.replace("/app/output", "/output")
                else:
                    # 相对路径，构建完整 URL
                    url_path = f"/output/images/{task_id}/{path.split('/')[-1]}"
                generated_image_urls.append(url_path)

        return {
            "task_id": task.task_id,
            "status": task.status,
            "url": task.url,
            "original_title": task.original_title,
            "original_desc": task.original_desc,
            "original_tags": task.original_tags,
            "original_images": task.original_images,
            "generated_title": task.generated_title,
            "generated_titles": task.generated_titles,  # 所有标题选项
            "generated_desc": task.generated_desc,
            "generated_images": generated_image_urls,  # 转换后的 URL
            "error_message": task.error_message,
            "created_at": task.created_at.isoformat() if task.created_at else None,
            "completed_at": task.completed_at.isoformat() if task.completed_at else None,
        }
    finally:
        db.close()


@router.get("/history", response_model=HistoryResponse)
async def get_history(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    status: Optional[TaskStatus] = None,
    user: dict = Depends(get_current_user),
):
    """获取历史记录"""
    db = SessionLocal()
    try:
        query = db.query(Task).filter(Task.user_id == user["user_id"]).order_by(desc(Task.created_at))

        if status:
            query = query.filter(Task.status == status.value)

        total = query.count()
        items = query.offset((page - 1) * page_size).limit(page_size).all()

        return HistoryResponse(
            total=total,
            items=[
                HistoryItem(
                    task_id=item.task_id,
                    url=item.url,
                    original_title=item.original_title or "",
                    generated_title=item.generated_title,
                    status=TaskStatus(item.status),
                    created_at=item.created_at,
                    completed_at=item.completed_at,
                )
                for item in items
            ],
        )
    finally:
        db.close()


@router.delete("/task/{task_id}")
async def delete_task(task_id: str, user: dict = Depends(get_current_user)):
    """删除任务"""
    db = SessionLocal()
    try:
        task = db.query(Task).filter(Task.task_id == task_id, Task.user_id == user["user_id"]).first()
        if not task:
            raise HTTPException(status_code=404, detail="任务不存在")

        db.delete(task)
        db.commit()
        return {"message": "任务已删除"}
    finally:
        db.close()
