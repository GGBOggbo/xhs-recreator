"""
工具函数
"""
import hashlib
import re
from datetime import datetime
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

import httpx


def generate_filename(prefix: str, extension: str = "png") -> str:
    """生成唯一文件名"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{prefix}_{timestamp}.{extension}"


def sanitize_filename(name: str, max_length: int = 50) -> str:
    """清理文件名，移除非法字符"""
    # 移除非法字符
    name = re.sub(r'[<>:"/\\|?*]', "", name)
    # 替换空格
    name = name.replace(" ", "_")
    # 限制长度
    if len(name) > max_length:
        name = name[:max_length]
    return name


async def download_image(url: str, save_path: Path) -> bool:
    """下载图片"""
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(url)
            response.raise_for_status()

            with open(save_path, "wb") as f:
                f.write(response.content)
            return True
    except Exception as e:
        print(f"Failed to download image: {e}")
        return False


def extract_note_id(url: str) -> Optional[str]:
    """从小红书链接提取笔记 ID"""
    # 匹配 /explore/{note_id} 格式
    match = re.search(r"/explore/([a-f0-9]+)", url)
    if match:
        return match.group(1)
    return None


def file_hash(file_path: Path) -> str:
    """计算文件 MD5 哈希"""
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()
