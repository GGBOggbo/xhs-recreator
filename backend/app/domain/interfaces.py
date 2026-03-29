"""
领域接口定义 — 用 Protocol 定义服务边界，不引入框架依赖
"""
from typing import Protocol, Optional, runtime_checkable
from pathlib import Path


@runtime_checkable
class NoteData(Protocol):
    """笔记数据协议 — 核心字段，保持宽松，后续按需扩展"""
    note_id: str
    url: str
    title: str
    description: str
    tags: list[str]
    images: list[str]
    author_name: str
    author_id: str
    like_count: int
    collect_count: int
    comment_count: int
    share_count: int
    note_type: str


@runtime_checkable
class CrawlerProvider(Protocol):
    """爬虫服务提供者接口 — 所有 crawler adapter 必须实现"""

    def fetch_note(
        self, url: str, cookies: Optional[str] = None
    ) -> tuple[bool, str, Optional[NoteData]]: ...

    def download_images(
        self, images: list[str], save_dir: Path
    ) -> list[Path]: ...
