"""
图片生成服务 - 使用 Nano Banana 2 生成图片
API 文档：https://grsai.dakka.com.cn
"""
import httpx
import base64
from pathlib import Path
from typing import Optional
import json
import asyncio

from loguru import logger

from app.config import settings, prompt_config


class ImageGenService:
    """Nano Banana 2 图片生成服务"""

    def __init__(self):
        self.api_key = settings.nanobanana_api_key
        # 国内直连地址
        self.base_url = "https://grsai.dakka.com.cn"
        # 默认模型从配置读取
        self.default_model = prompt_config.image_model

    async def generate_image(
        self,
        prompt: str,
        save_path: Path,
        model: Optional[str] = None,
        aspect_ratio: str = "3:4",
        image_size: str = "1K",
        reference_urls: Optional[list[str]] = None,
        style: Optional[str] = None
    ) -> tuple[bool, str, Optional[Path]]:
        """
        生成图片

        Args:
            prompt: 生成提示词
            save_path: 保存路径
            model: 模型名称，可选 nano-banana-2 或 nano-banana-pro
            aspect_ratio: 宽高比，默认 3:4（小红书标准）
            image_size: 图片大小 "1K" / "2K" / "4K"
            reference_urls: 参考图URL列表
            style: 额外风格描述

        Returns:
            (success, message, image_path)
        """
        try:
            # 使用传入的模型或默认模型
            use_model = model or self.default_model

            # 直接使用传入的 prompt（已在 task_runner 中拼接好风格+内容）
            full_prompt = prompt
            if style:
                full_prompt = f"{prompt}, {style}"

            # 构建请求参数
            request_data = {
                "model": use_model,
                "prompt": full_prompt,
                "aspectRatio": aspect_ratio,
                "imageSize": image_size,
                "shutProgress": False,  # 获取进度
            }

            # 添加参考图
            if reference_urls:
                request_data["urls"] = reference_urls

            # 调用 Nano Banana API
            async with httpx.AsyncClient(timeout=180) as client:
                response = await client.post(
                    f"{self.base_url}/v1/draw/nano-banana",
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {self.api_key}"
                    },
                    json=request_data
                )

                if response.status_code != 200:
                    error_detail = response.text
                    logger.error(f"Nano Banana API 错误: {error_detail}")
                    return False, f"API 调用失败: {response.status_code} - {error_detail}", None

                # 处理流式响应
                result = await self._process_stream_response(response, save_path)

                if result:
                    return True, "成功", result
                else:
                    return False, "图片生成失败", None

        except Exception as e:
            error_msg = f"图片生成失败: {str(e)}"
            logger.error(error_msg)
            return False, error_msg, None

    async def _process_stream_response(
        self,
        response: httpx.Response,
        save_path: Path
    ) -> Optional[Path]:
        """
        处理流式响应，等待图片生成完成

        Args:
            response: HTTP 响应
            save_path: 保存路径

        Returns:
            保存的图片路径
        """
        try:
            image_url = None

            # 读取流式响应
            async for line in response.aiter_lines():
                if not line or line.startswith(":"):
                    continue

                # 去掉 SSE 格式的 'data: ' 前缀
                if line.startswith("data: "):
                    line = line[6:]

                try:
                    # 解析 JSON
                    data = json.loads(line)

                    status = data.get("status", "")
                    progress = data.get("progress", 0)

                    logger.info(f"Nano Banana 进度: {progress}%, 状态: {status}")

                    if status == "succeeded":
                        results = data.get("results", [])
                        if results and len(results) > 0:
                            image_url = results[0].get("url", "")
                            break

                    elif status == "failed":
                        failure_reason = data.get("failure_reason", "")
                        error = data.get("error", "")
                        logger.error(f"图片生成失败: {failure_reason} - {error}")
                        return None

                except json.JSONDecodeError:
                    continue

            if not image_url:
                logger.error("未获取到图片 URL")
                return None

            # 下载图片
            return await self._download_image(image_url, save_path)

        except Exception as e:
            logger.error(f"处理流式响应失败: {e}")
            return None

    async def _download_image(
        self,
        image_url: str,
        save_path: Path
    ) -> Optional[Path]:
        """
        下载图片到本地

        Args:
            image_url: 图片 URL
            save_path: 保存路径

        Returns:
            保存的图片路径
        """
        try:
            async with httpx.AsyncClient(timeout=60) as client:
                response = await client.get(image_url)
                response.raise_for_status()

                # 确保目录存在
                save_path.parent.mkdir(parents=True, exist_ok=True)

                # 保存图片
                save_path.write_bytes(response.content)

                logger.info(f"图片下载成功: {save_path}")
                return save_path

        except Exception as e:
            logger.error(f"下载图片失败: {e}")
            return None

    async def generate_with_polling(
        self,
        prompt: str,
        save_path: Path,
        aspect_ratio: str = "3:4",
        reference_urls: Optional[list[str]] = None,
        style: Optional[str] = None,
        max_wait: int = 120
    ) -> tuple[bool, str, Optional[Path]]:
        """
        使用轮询方式生成图片（适用于需要回调的场景）

        Args:
            prompt: 生成提示词
            save_path: 保存路径
            aspect_ratio: 宽高比
            reference_urls: 参考图URL列表
            style: 额外风格描述
            max_wait: 最大等待时间（秒）

        Returns:
            (success, message, image_path)
        """
        try:
            # 直接使用传入的 prompt（已在 task_runner 中拼接好风格+内容）
            full_prompt = prompt
            if style:
                full_prompt = f"{prompt}, {style}"

            request_data = {
                "model": self.default_model,
                "prompt": full_prompt,
                "aspectRatio": aspect_ratio,
                "imageSize": "1K",
                "shutProgress": True,
                "webHook": "-1"  # 立即返回任务 ID
            }

            if reference_urls:
                request_data["urls"] = reference_urls

            # 提交任务
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(
                    f"{self.base_url}/v1/draw/nano-banana",
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {self.api_key}"
                    },
                    json=request_data
                )

                if response.status_code != 200:
                    return False, f"提交任务失败: {response.status_code}", None

                result = response.json()
                task_id = result.get("data", {}).get("id", "")

                if not task_id:
                    return False, "未获取到任务 ID", None

            # 轮询结果
            waited = 0
            poll_interval = 3

            while waited < max_wait:
                await asyncio.sleep(poll_interval)
                waited += poll_interval

                async with httpx.AsyncClient(timeout=30) as client:
                    response = await client.post(
                        f"{self.base_url}/v1/draw/result",
                        headers={
                            "Content-Type": "application/json",
                            "Authorization": f"Bearer {self.api_key}"
                        },
                        json={"id": task_id}
                    )

                    if response.status_code != 200:
                        continue

                    result = response.json()
                    data = result.get("data", {})
                    status = data.get("status", "")

                    logger.info(f"轮询进度: {data.get('progress', 0)}%")

                    if status == "succeeded":
                        results = data.get("results", [])
                        if results and len(results) > 0:
                            image_url = results[0].get("url", "")
                            return True, "成功", await self._download_image(image_url, save_path)

                    elif status == "failed":
                        return False, f"生成失败: {data.get('error', '')}", None

            return False, "生成超时", None

        except Exception as e:
            error_msg = f"图片生成失败: {str(e)}"
            logger.error(error_msg)
            return False, error_msg, None

    async def generate_images(
        self,
        prompts: list[str],
        save_dir: Path,
        aspect_ratio: str = "3:4",
        style: Optional[str] = None
    ) -> list[tuple[bool, str, Optional[Path]]]:
        """
        批量生成图片

        Args:
            prompts: 提示词列表
            save_dir: 保存目录
            aspect_ratio: 宽高比
            style: 额外风格描述

        Returns:
            每张图片的生成结果列表
        """
        results = []
        for i, prompt in enumerate(prompts):
            save_path = save_dir / f"generated_{i}.png"
            result = await self.generate_image(
                prompt,
                save_path,
                aspect_ratio=aspect_ratio,
                style=style
            )
            results.append(result)
        return results


# 全局实例
image_gen_service = ImageGenService()
