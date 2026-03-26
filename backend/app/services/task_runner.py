"""
任务调度服务 - 异步处理任务并推送进度
"""
import asyncio
from datetime import datetime
from pathlib import Path
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

from app.services.vision import vision_service
from app.services.llm import llm_service
from app.services.image_gen import image_gen_service
from app.api.websocket import broadcast_progress


class TaskRunner:
    """任务执行器"""

    def __init__(self):
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
        vision_model: str = "glm-4.6v-flash"
    ):
        """
        执行完整任务流程（同步版本，供后台任务调用）

        Args:
            task: 任务对象
            db: 数据库会话
            image_count: 要处理的图片数量
            selected_indices: 选中的图片索引列表
            user_prompt: 用户自定义提示词
            image_model: 图片生成模型 (nano-banana-2 或 nano-banana-pro)
            image_ratio: 输出图像比例 (auto/1:1/3:4/4:3/9:16/16:9)
            vision_model: 视觉分析模型 (glm-4v-flash / glm-4v-plus)
        """
        return await self._run_task_async(task, db, image_count, selected_indices, user_prompt, image_model, image_ratio, vision_model)

    async def _run_task_async(
        self,
        task: Task,
        db: Session,
        image_count: int = 1,
        selected_indices: list[int] = None,
        user_prompt: str = "",
        image_model: str = "nano-banana-2",
        image_ratio: str = "3:4",
        vision_model: str = "glm-4.6v-flash"
    ):
        """
        执行完整任务流程（内部异步实现）

        Args:
            task: 任务对象
            db: 数据库会话
            image_count: 要处理的图片数量
            selected_indices: 选中的图片索引列表
            user_prompt: 用户自定义提示词
            image_model: 图片生成模型
            image_ratio: 输出图像比例
            vision_model: 视觉分析模型
        """
        if selected_indices is None:
            selected_indices = list(range(image_count))
        task_id = task.task_id

        try:
            # ========== Phase 1: 爬取内容 ==========
            await self._update_status(db, task, TaskStatus.FETCHING, 5, "正在获取笔记内容...")

            success, msg, note_content = spider_service.fetch_note(task.url)
            if not success:
                await self._fail_task(db, task, msg)
                return

            # 更新原始内容
            task.original_title = note_content.title
            task.original_desc = note_content.description
            task.original_tags = note_content.tags
            # 根据选中的索引获取对应的图片
            all_images = note_content.images
            task.original_images = [all_images[i] for i in selected_indices if i < len(all_images)]
            db.commit()

            await broadcast_progress(
                task_id,
                TaskStatus.FETCHING.value,
                15,
                "笔记内容获取完成",
                f"标题: {note_content.title[:30]}..."
            )

            # ========== Phase 2: 图片分析 ==========
            await self._update_status(db, task, TaskStatus.ANALYZING, 20, "正在分析图片...")

            # 获取实际要处理的图片数量
            actual_image_count = len(task.original_images)

            # 下载图片到本地
            image_save_dir = self.output_dir / "images" / task_id
            local_images = spider_service.download_images(
                task.original_images,
                image_save_dir
            )

            # 分析每张图片
            image_descriptions = []
            for i, img_path in enumerate(local_images):
                progress = 20 + (i + 1) / len(local_images) * 20
                await broadcast_progress(
                    task_id,
                    TaskStatus.ANALYZING.value,
                    int(progress),
                    f"正在分析图片 {i+1}/{len(local_images)}",
                    str(img_path.name)
                )

                success, msg, desc = vision_service.analyze_image(img_path, model=vision_model)
                if not success:
                    # 图片分析失败，整体任务失败
                    raise Exception(f"图片分析失败: {msg}")
                if desc:
                    image_descriptions.append(desc)

            await broadcast_progress(
                task_id,
                TaskStatus.ANALYZING.value,
                40,
                "图片分析完成",
                f"共分析 {len(image_descriptions)} 张图片"
            )

            # ========== Phase 3: 文案二创 ==========
            await self._update_status(db, task, TaskStatus.WRITING, 45, "正在生成标题...")

            # 生成标题
            success, _, titles = llm_service.generate_titles(
                task.original_title,
                task.original_desc,
                task.original_tags,
                user_prompt
            )

            await broadcast_progress(
                task_id,
                TaskStatus.WRITING.value,
                55,
                "标题生成完成",
                f"生成 {len(titles) if titles else 0} 个标题变体"
            )

            # 改写文案
            await broadcast_progress(task_id, TaskStatus.WRITING.value, 60, "正在改写文案...")
            success, _, new_content = llm_service.rewrite_content(
                task.original_title,
                task.original_desc,
                task.original_tags,
                user_prompt
            )

            # 选择第一个标题作为主标题，同时存储所有标题选项
            if titles and len(titles) > 0:
                task.generated_title = titles[0].get("title", task.original_title)
                task.generated_titles = titles  # 存储所有标题
            else:
                task.generated_title = task.original_title
                task.generated_titles = [{"title": task.original_title, "type": "原始", "trigger": "保留原样"}]

            task.generated_desc = new_content or task.original_desc
            db.commit()

            await broadcast_progress(
                task_id,
                TaskStatus.WRITING.value,
                70,
                "文案二创完成",
                "标题和正文已生成"
            )

            # ========== Phase 4: 图片生成（并发） ==========
            await self._update_status(db, task, TaskStatus.GENERATING, 75, "正在生成图片...")

            # 直接拼接：风格描述 + 图片内容描述
            style_desc = prompt_config.image_style
            content_desc = " ".join(image_descriptions)
            image_prompt = f"{style_desc}\n\n图片内容：{content_desc}"

            # 并发生成所有图片
            await broadcast_progress(
                task_id,
                TaskStatus.GENERATING.value,
                75,
                f"正在并发生成 {actual_image_count} 张图片",
                "AI 创作中..."
            )

            async def generate_single_image(index: int):
                """生成单张图片"""
                save_path = self.output_dir / "images" / task_id / f"generated_{index}.png"
                success, _, img_path = await image_gen_service.generate_image(
                    image_prompt,
                    save_path,
                    model=image_model,
                    aspect_ratio=image_ratio
                )
                return (index, success, str(img_path) if success and img_path else None)

            # 创建所有生成任务
            tasks = [generate_single_image(i) for i in range(actual_image_count)]

            # 并发执行
            results = await asyncio.gather(*tasks)

            # 按顺序整理结果
            generated_images = []
            for index, success, img_path in sorted(results):
                if success and img_path:
                    generated_images.append(img_path)

            task.generated_images = generated_images
            db.commit()

            # ========== Phase 5: 完成 ==========
            await self._update_status(db, task, TaskStatus.COMPLETED, 100, "任务完成！")
            task.completed_at = datetime.utcnow()
            db.commit()

            # 保存文本结果
            await self._save_text_result(task)

            await broadcast_progress(
                task_id,
                TaskStatus.COMPLETED.value,
                100,
                "二创完成！",
                "可以查看结果了"
            )

            logger.info(f"任务完成: {task_id}")

        except Exception as e:
            error_msg = f"任务执行异常: {str(e)}"
            logger.error(error_msg)
            await self._fail_task(db, task, error_msg)

    async def _update_status(
        self,
        db: Session,
        task: Task,
        status: TaskStatus,
        progress: int,
        message: str
    ):
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
            task.task_id,
            TaskStatus.FAILED.value,
            0,
            "任务失败",
            error_msg
        )

    async def _save_text_result(self, task: Task):
        """保存文本结果到文件"""
        try:
            save_dir = self.output_dir / "texts" / task.task_id
            save_dir.mkdir(parents=True, exist_ok=True)

            # 保存标题
            title_file = save_dir / "title.txt"
            title_file.write_text(task.generated_title or "", encoding="utf-8")

            # 保存正文（包含标签）
            content = f"{task.generated_title}\n\n{task.generated_desc}\n\n"
            if task.original_tags:
                tags_text = " ".join(f"#{tag}" for tag in task.original_tags)
                content += tags_text

            content_file = save_dir / "content.txt"
            content_file.write_text(content, encoding="utf-8")

            logger.info(f"文本结果已保存: {save_dir}")

        except Exception as e:
            logger.error(f"保存文本结果失败: {e}")


# 全局实例
task_runner = TaskRunner()
