"""
数据模型定义
"""
from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class TaskStatus(str, Enum):
    """任务状态"""
    PENDING = "pending"
    FETCHING = "fetching"       # 爬取中
    ANALYZING = "analyzing"     # 分析图片中
    GENERATING = "generating"   # 生成图片中
    WRITING = "writing"         # 生成文案中
    COMPLETED = "completed"
    FAILED = "failed"


class Task(Base):
    """任务数据库模型"""
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(String(36), unique=True, nullable=False, index=True)
    url = Column(String(512), nullable=False)
    status = Column(String(20), default=TaskStatus.PENDING.value)

    # 原始内容
    original_title = Column(String(255))
    original_desc = Column(Text)
    original_tags = Column(JSON)  # List[str]
    original_images = Column(JSON)  # List[str] - 图片URL

    # 生成内容
    generated_title = Column(String(255))  # 主标题（用户选择的）
    generated_titles = Column(JSON)  # List[dict] - 所有标题选项
    generated_desc = Column(Text)
    generated_images = Column(JSON)  # List[str] - 本地路径

    # 元数据
    user_prompt = Column(Text)  # 用户自定义提示词
    image_count = Column(Integer, default=1)  # 要处理的图片数量
    image_model = Column(String(50), default="nano-banana-2")  # 图片生成模型
    vision_model = Column(String(50), default="glm-4.6v-flash")  # 视觉分析模型
    image_style_id = Column(String(30), default="notebook")  # 图片风格ID
    error_message = Column(Text)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)


# ============ Pydantic 请求/响应模型 ============

class CreateTaskRequest(BaseModel):
    """创建任务请求"""
    url: str = Field(..., description="小红书笔记链接")
    image_count: int = Field(default=1, ge=1, le=9, description="要处理的图片数量")
    selected_indices: Optional[list[int]] = Field(default=None, description="选中的图片索引")
    user_prompt: Optional[str] = Field(default="", description="用户自定义提示词")
    image_model: Optional[str] = Field(default="nano-banana-2", description="图片生成模型")
    image_ratio: Optional[str] = Field(default="3:4", description="输出图像比例")
    vision_model: Optional[str] = Field(default="glm-4.6v-flash", description="视觉分析模型")
    image_style_id: Optional[str] = Field(default="notebook", description="图片风格ID (notebook/whiteboard)")


class TaskProgress(BaseModel):
    """任务进度"""
    task_id: str
    status: TaskStatus
    progress: int = Field(..., ge=0, le=100, description="进度百分比")
    message: str = ""
    current_step: str = ""


class NoteContent(BaseModel):
    """笔记内容"""
    title: str
    description: str
    tags: list[str]
    images: list[str]
    author: str
    author_id: str


class TaskResult(BaseModel):
    """任务结果"""
    task_id: str
    original: NoteContent
    generated: dict


class TaskResponse(BaseModel):
    """任务响应"""
    task_id: str
    status: TaskStatus
    message: str = ""


class HistoryItem(BaseModel):
    """历史记录项"""
    task_id: str
    url: str
    original_title: str
    generated_title: Optional[str]
    status: TaskStatus
    created_at: datetime
    completed_at: Optional[datetime]


class HistoryResponse(BaseModel):
    """历史记录响应"""
    total: int
    items: list[HistoryItem]
