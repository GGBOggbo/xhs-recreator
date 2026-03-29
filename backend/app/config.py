"""
配置管理模块
"""
import os
from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings
from pydantic import Field
import yaml


class Settings(BaseSettings):
    """应用配置"""

    # API Keys
    zhipu_api_key: str = Field(default="", alias="ZHIPU_API_KEY")
    nanobanana_api_key: str = Field(default="", alias="NANOBANANA_API_KEY")
    xhs_cookies: str = Field(default="", alias="XHS_COOKIES")

    # 路径配置
    base_dir: Path = Field(default_factory=lambda: Path(__file__).parent.parent.parent)
    output_dir: Path = Field(default_factory=lambda: Path(__file__).parent.parent.parent / "output")
    data_dir: Path = Field(default_factory=lambda: Path(__file__).parent.parent.parent / "data")
    spider_xhs_path: Path = Field(default_factory=lambda: Path(__file__).parent.parent.parent / "spider_xhs")

    # 数据库 - 使用绝对路径
    database_url: str = Field(default="sqlite:////app/data/history.db")

    # 服务配置
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


class PromptConfig:
    """提示词配置"""

    def __init__(self, config_path: Optional[Path] = None):
        if config_path is None:
            config_path = Path(__file__).parent.parent / "prompts.yaml"

        self.config_path = config_path
        self._config = self._load_config()

    def _load_config(self) -> dict:
        """加载配置文件"""
        if not self.config_path.exists():
            return self._default_config()

        with open(self.config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def _default_config(self) -> dict:
        """默认配置"""
        return {
            "system_prompt": "你是一个小红书文案二创助手，擅长将原始内容改写成更有吸引力的文案。",
            "vision_prompt": "请详细描述这张图片的内容，包括主体、场景、风格、色调等关键信息。",
            "image_style": "cartoon",
        }

    @property
    def system_prompt(self) -> str:
        return self._config.get("system_prompt", "")

    @property
    def vision_prompt(self) -> str:
        return self._config.get("vision_prompt", "")

    @property
    def content_prompt(self) -> str:
        """文案改写提示词"""
        return self._config.get("content_prompt", "你是小红书文案改写专家。")

    @property
    def image_style(self) -> str:
        return self._config.get("image_style", "cartoon")

    def get_image_style(self, style_id: str = "notebook") -> str:
        """根据 style_id 获取对应风格的提示词"""
        styles = self._config.get("image_styles", [])
        for s in styles:
            if s.get("id") == style_id:
                return self._config.get(s["key"], self.image_style)
        # fallback to default
        return self.image_style

    @property
    def image_styles_list(self) -> list[dict]:
        """返回可选风格列表"""
        return self._config.get("image_styles", [
            {"id": "notebook", "name": "学霸笔记风", "description": "默认风格", "key": "image_style"}
        ])

    @property
    def image_model(self) -> str:
        """图片生成模型"""
        return self._config.get("image_model", "nano-banana-fast")

    @property
    def image_aspect_ratio(self) -> str:
        """默认图片比例"""
        return self._config.get("image_aspect_ratio", "3:4")

    @property
    def image_size(self) -> str:
        """默认图片分辨率"""
        return self._config.get("default_image_size", "1K")

    @property
    def vision_model(self) -> str:
        """视觉分析模型"""
        return self._config.get("vision_model", "glm-4.6v-flash")


# 全局配置实例
settings = Settings()
prompt_config = PromptConfig()
