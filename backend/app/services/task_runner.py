"""
任务编排服务 — 负责状态更新 / DB commit / 进度推送 / 异常兜底
具体业务逻辑在 application/steps.py
"""
from datetime import datetime
from typing import Optional

from loguru import logger
from sqlalchemy.orm import Session

from app.config import settings, prompt_config
from app.models.task import Task, TaskStatus

# 延迟导入 spider，避免导入错误
try:
    from app.services.spider import spider_service
except Exception as e:
    spider_service = None
    logger.warning(f"Spider service not available: {e}")

from app.domain.interfaces import CrawlerProvider

from app.services.vision import vision_service
from app.services.llm import llm_service
from app.services.image_gen import image_gen_service
from app.api.websocket import broadcast_progress
from app.application.steps import (
    fetch_note_step,
    analyze_images_step,
    rewrite_content_step,
    generate_images_step,
    save_result_step,
)


class TaskRunner:
    """任务编排器 — 只负责流程控制，不包含业务细节"""

    def __init__(self, crawler: CrawlerProvider = spider_service):
        self.crawler = crawler
        self.output_dir = settings.output_dir

    async def run_task(
        self,
        task: Task,
        db: Session,
        image_count: int = 1,
        selected_indices: list[int] = None,
        user_prompt: str = "",
        image_model: str = "nano-banana-2",
        image_ratio: str = "3:4",
        vision_model: str = "glm-4.6v-flash",
        image_style_id: str = "notebook",
        cookies_plain: str = "",
    ):
        """执行完整任务流程（供后台任务调用）"""
        return await self._run_task_async(task, db, image_count, selected_indices, user_prompt, image_model, image_ratio, vision_model, image_style_id, cookies_plain)

    async def _run_task_async(
        self,
        task: Task,
        db: Session,
        image_count: int = 1,
        selected_indices: list[int] = None,
        user_prompt: str = "",
        image_model: str = "nano-banana-2",
        image_ratio: str = "3:4",
        vision_model: str = "glm-4.6v-flash",
        image_style_id: str = "notebook",
        cookies_plain: str = "",
    ):
        if selected_indices is None:
            selected_indices = list(range(image_count))
        task_id = task.task_id

        try:
            # ========== Phase 1: 爬取内容 ==========
            await self._update_status(db, task, TaskStatus.FETCHING, 5, "正在获取笔记内容...")

            note_data, selected_images = await fetch_note_step(self.crawler, task.url, selected_indices, cookies=cookies_plain)

            # 保存爬取结果到 DB
            task.original_title = note_data.title
            task.original_desc = note_data.description
            task.original_tags = note_data.tags
            task.original_images = selected_images
            db.commit()

            await broadcast_progress(
                task_id, TaskStatus.FETCHING.value, 15,
                "笔记内容获取完成", f"标题: {note_data.title[:30]}..."
            )

            # ========== Phase 2: 图片分析 ==========
            await self._update_status(db, task, TaskStatus.ANALYZING, 20, "正在分析图片...")

            actual_count = len(selected_images)
            image_save_dir = self.output_dir / "images" / task_id

            local_images, descriptions = await analyze_images_step(
                self.crawler, vision_service, selected_images, image_save_dir, vision_model
            )

            await broadcast_progress(
                task_id, TaskStatus.ANALYZING.value, 40,
                "图片分析完成", f"共分析 {len(descriptions)} 张图片"
            )

            # ========== Phase 3: 文案二创 ==========
            await self._update_status(db, task, TaskStatus.WRITING, 45, "正在生成标题...")

            titles, new_content = await rewrite_content_step(
                llm_service, task.original_title, task.original_desc, task.original_tags, user_prompt
            )

            # 保存改写结果到 DB
            if titles:
                task.generated_title = titles[0].get("title", task.original_title)
                task.generated_titles = titles
            else:
                task.generated_title = task.original_title
                task.generated_titles = [{"title": task.original_title, "type": "原始", "trigger": "保留原样"}]

            task.generated_desc = new_content
            db.commit()

            await broadcast_progress(
                task_id, TaskStatus.WRITING.value, 70,
                "文案二创完成", "标题和正文已生成"
            )

            # ========== Phase 4: 图片生成 ==========
            await self._update_status(db, task, TaskStatus.GENERATING, 75, "正在生成图片...")

            # 拼接提示词：风格 + 内容
            style_desc = prompt_config.get_image_style(image_style_id)
            content_desc = " ".join(descriptions)
            image_prompt = f"{style_desc}\n\n图片内容：{content_desc}"

            await broadcast_progress(
                task_id, TaskStatus.GENERATING.value, 75,
                f"正在并发生成 {actual_count} 张图片", "AI 创作中..."
            )

            generated_images = await generate_images_step(
                image_gen_service, image_prompt, task_id, actual_count,
                self.output_dir, image_model, image_ratio
            )

            task.generated_images = generated_images
            db.commit()

            # ========== Phase 5: 完成 ==========
            await self._update_status(db, task, TaskStatus.COMPLETED, 100, "任务完成！")
            task.completed_at = datetime.utcnow()
            db.commit()

            save_result_step(task, self.output_dir)

            await broadcast_progress(
                task_id, TaskStatus.COMPLETED.value, 100,
                "二创完成！", "可以查看结果了"
            )

            logger.info(f"任务完成: {task_id}")

        except Exception as e:
            error_msg = f"任务执行异常: {str(e)}"
            logger.error(error_msg)
            await self._fail_task(db, task, error_msg)

    async def _update_status(self, db: Session, task: Task, status: TaskStatus, progress: int, message: str):
        """更新任务状态"""
        task.status = status.value
        task.updated_at = datetime.utcnow()
        db.commit()
        logger.info(f"Task {task.task_id}: {status.value} - {message}")

    async def _fail_task(self, db: Session, task: Task, error_msg: str):
        """标记任务失败"""
        task.status = TaskStatus.FAILED.value
        task.error_message = error_msg
        task.updated_at = datetime.utcnow()
        db.commit()

        await broadcast_progress(
            task.task_id, TaskStatus.FAILED.value, 0,
            "任务失败", error_msg
        )


# 全局实例
task_runner = TaskRunner()
