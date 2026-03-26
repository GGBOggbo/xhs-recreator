"""
图片分析服务 - 使用智谱 GLM-4V 多模态模型分析图片内容
"""
import base64
import time
from pathlib import Path
from typing import Optional

from loguru import logger
from zhipuai import ZhipuAI

from app.config import settings, prompt_config


class VisionService:
    """图片分析服务 - 使用智谱 GLM-4.6V 多模态模型"""

    def __init__(self):
        self.client = ZhipuAI(api_key=settings.zhipu_api_key)
        # 默认模型从配置读取
        # 可选模型: glm-4.6v-flash (免费), glm-4.6v (旗舰版)
        self.default_model = prompt_config.vision_model
        # 重试配置
        self.max_retries = 5
        self.retry_delay = 2  # 秒

    def encode_image(self, image_path: Path) -> str:
        """将图片编码为 base64（纯字符串，不带前缀）"""
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")

    def analyze_image(
        self,
        image_path: Path,
        custom_prompt: Optional[str] = None,
        model: Optional[str] = None
    ) -> tuple[bool, str, Optional[str]]:
        """
        分析图片内容（带重试机制）

        Args:
            image_path: 图片路径
            custom_prompt: 自定义提示词
            model: 模型名称 (glm-4v-flash / glm-4v-plus / glm-4v-plus-0111)

        Returns:
            (success, message, description)
        """
        last_error = None

        for attempt in range(1, self.max_retries + 1):
            try:
                # 读取图片（纯 base64 字符串）
                image_base64 = self.encode_image(image_path)

                # 构建提示词
                prompt = custom_prompt or prompt_config.vision_prompt

                # 使用传入的模型或默认模型
                use_model = model or self.default_model

                # 调用 GLM-4.6V API（遵循官方规范：text 在前，image_url 在后）
                response = self.client.chat.completions.create(
                    model=use_model,
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": prompt
                                },
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": image_base64
                                    }
                                }
                            ]
                        }
                    ],
                )

                description = response.choices[0].message.content
                logger.info(f"图片分析成功: {image_path.name}, 模型: {use_model}")
                return True, "成功", description

            except Exception as e:
                last_error = str(e)
                logger.warning(f"图片分析失败 (尝试 {attempt}/{self.max_retries}): {last_error}")

                # 如果不是最后一次尝试，等待后重试
                if attempt < self.max_retries:
                    logger.info(f"等待 {self.retry_delay} 秒后重试...")
                    time.sleep(self.retry_delay)

        # 所有重试都失败
        error_msg = f"图片分析失败 (已重试{self.max_retries}次): {last_error}"
        logger.error(error_msg)
        return False, error_msg, None

    def analyze_image_url(
        self,
        image_url: str,
        custom_prompt: Optional[str] = None,
        model: Optional[str] = None
    ) -> tuple[bool, str, Optional[str]]:
        """
        通过URL分析图片内容

        Args:
            image_url: 图片URL
            custom_prompt: 自定义提示词
            model: 模型名称

        Returns:
            (success, message, description)
        """
        try:
            prompt = custom_prompt or prompt_config.vision_prompt
            use_model = model or self.default_model

            response = self.client.chat.completions.create(
                model=use_model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": image_url
                                }
                            },
                            {
                                "type": "text",
                                "text": prompt
                            }
                        ]
                    }
                ],
            )

            description = response.choices[0].message.content
            logger.info(f"图片URL分析成功, 模型: {use_model}")
            return True, "成功", description

        except Exception as e:
            error_msg = f"图片URL分析失败: {str(e)}"
            logger.error(error_msg)
            return False, error_msg, None

    def analyze_multiple_images(
        self,
        image_paths: list[Path],
        custom_prompt: Optional[str] = None,
        model: Optional[str] = None
    ) -> list[tuple[bool, str, Optional[str]]]:
        """
        批量分析多张图片

        Args:
            image_paths: 图片路径列表
            custom_prompt: 自定义提示词
            model: 模型名称

        Returns:
            每张图片的分析结果列表
        """
        results = []
        for path in image_paths:
            result = self.analyze_image(path, custom_prompt, model)
            results.append(result)
        return results


# 全局实例
vision_service = VisionService()
