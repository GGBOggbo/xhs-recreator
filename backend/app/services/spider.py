"""
爬虫服务封装 - 调用 Spider_XHS 获取小红书笔记内容
"""
import sys
from pathlib import Path
from typing import Optional
from dataclasses import dataclass

from loguru import logger

# 添加 spider_xhs 到路径
spider_xhs_path = Path(__file__).parent.parent.parent.parent / "spider_xhs"
if spider_xhs_path.exists():
    sys.path.insert(0, str(spider_xhs_path))

from apis.xhs_pc_apis import XHS_Apis
from xhs_utils.data_util import handle_note_info

from app.config import settings


@dataclass
class NoteContent:
    """笔记内容数据结构"""
    note_id: str
    url: str
    title: str
    description: str
    tags: list[str]
    images: list[str]  # 图片URL列表
    author_name: str
    author_id: str
    like_count: int
    collect_count: int
    comment_count: int
    share_count: int
    note_type: str  # "video" or "normal"
    video_url: Optional[str] = None


class SpiderXHSAdapter:
    """爬虫适配器 — 实现 CrawlerProvider 接口，封装 Spider_XHS"""

    def __init__(self):
        self.xhs_apis = XHS_Apis()
        self.cookies = settings.xhs_cookies

    def fetch_note(self, url: str, cookies: Optional[str] = None) -> tuple[bool, str, Optional[NoteContent]]:
        """
        爬取笔记内容

        Args:
            url: 小红书笔记链接
            cookies: 可选的 cookies，不传则使用配置文件中的

        Returns:
            (success, message, NoteContent)
        """
        cookies_str = cookies or self.cookies
        if not cookies_str:
            return False, "未配置小红书 Cookies", None

        try:
            success, msg, note_info = self.xhs_apis.get_note_info(url, cookies_str)

            if not success:
                return False, f"获取笔记失败: {msg}", None

            if not note_info or "data" not in note_info:
                return False, "返回数据为空", None

            items = note_info.get("data", {}).get("items", [])
            if not items:
                return False, "未找到笔记内容", None

            # 解析笔记数据
            item = items[0]
            note_card = item.get("note_card", {})

            # 提取基本信息
            note_id = note_card.get("note_id", "")
            title = note_card.get("title", "")
            desc = note_card.get("desc", "")

            # 提取标签
            tags = []
            for tag in note_card.get("tag_list", []):
                tag_name = tag.get("name", "")
                if tag_name:
                    tags.append(tag_name)

            # 提取图片URL
            images = []
            image_list = note_card.get("image_list", [])
            for img in image_list:
                # 获取高清图片URL
                img_url = img.get("url_default", "") or img.get("url", "")
                if img_url:
                    # 转换为无水印URL
                    success, _, no_water_url = self.xhs_apis.get_note_no_water_img(img_url)
                    images.append(no_water_url if success else img_url)

            # 提取作者信息
            user = note_card.get("user", {})
            author_name = user.get("nickname", "")
            author_id = user.get("user_id", "")

            # 提取互动数据
            interact_info = note_card.get("interact_info", {})
            like_count = interact_info.get("liked_count", 0)
            collect_count = interact_info.get("collected_count", 0)
            comment_count = interact_info.get("comment_count", 0)
            share_count = interact_info.get("share_count", 0)

            # 笔记类型
            note_type = note_card.get("type", "normal")
            video_url = None
            if note_type == "video":
                video_info = note_card.get("video", {})
                video_url = video_info.get("media", {}).get("stream", {}).get("h264", [{}])[0].get("master_url", "")

            content = NoteContent(
                note_id=note_id,
                url=url,
                title=title,
                description=desc,
                tags=tags,
                images=images,
                author_name=author_name,
                author_id=author_id,
                like_count=like_count,
                collect_count=collect_count,
                comment_count=comment_count,
                share_count=share_count,
                note_type=note_type,
                video_url=video_url,
            )

            logger.info(f"成功爬取笔记: {note_id}, 标题: {title}, 图片数: {len(images)}")
            return True, "成功", content

        except Exception as e:
            error_msg = f"爬取笔记异常: {str(e)}"
            logger.error(error_msg)
            return False, error_msg, None

    def download_images(self, images: list[str], save_dir: Path) -> list[Path]:
        """
        下载图片到本地

        Args:
            images: 图片URL列表
            save_dir: 保存目录

        Returns:
            下载后的本地路径列表
        """
        import httpx

        save_dir.mkdir(parents=True, exist_ok=True)
        local_paths = []

        for i, url in enumerate(images):
            try:
                response = httpx.get(url, timeout=30, follow_redirects=True)
                response.raise_for_status()

                # 确定扩展名
                ext = ".jpg"
                content_type = response.headers.get("content-type", "")
                if "png" in content_type:
                    ext = ".png"
                elif "webp" in content_type:
                    ext = ".webp"

                save_path = save_dir / f"image_{i}{ext}"
                save_path.write_bytes(response.content)
                local_paths.append(save_path)
                logger.info(f"下载图片成功: {save_path}")

            except Exception as e:
                logger.error(f"下载图片失败 {url}: {e}")

        return local_paths


# 全局实例 — 实现 CrawlerProvider 接口
spider_service = SpiderXHSAdapter()
