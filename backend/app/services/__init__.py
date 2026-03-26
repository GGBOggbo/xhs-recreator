# Services module
# 注意：spider 依赖 spider_xhs 的 JS 文件，导入可能失败
try:
    from app.services.spider import spider_service, NoteContent
except Exception as e:
    spider_service = None
    NoteContent = None
    import warnings
    warnings.warn(f"Spider service not available: {e}")

from app.services.vision import vision_service
from app.services.llm import llm_service
from app.services.image_gen import image_gen_service
from app.services.task_runner import task_runner

__all__ = [
    "spider_service",
    "NoteContent",
    "vision_service",
    "llm_service",
    "image_gen_service",
    "task_runner",
]
