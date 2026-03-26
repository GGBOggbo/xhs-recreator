"""
文案二创服务 - 使用智谱 GLM-4 进行标题和文案的二次创作
"""
import json
from typing import Optional

from loguru import logger
from zhipuai import ZhipuAI

from app.config import settings, prompt_config


class LLMService:
    """文案二创服务"""

    def __init__(self):
        self.client = ZhipuAI(api_key=settings.zhipu_api_key)
        self.model = "glm-4-flash"  # 快速响应模型

    def generate_titles(
        self,
        original_title: str,
        original_desc: str,
        tags: list[str],
        user_prompt: Optional[str] = None
    ) -> tuple[bool, str, Optional[list[dict]]]:
        """
        生成爆款标题变体

        Args:
            original_title: 原始标题
            original_desc: 原始描述
            tags: 标签列表
            user_prompt: 用户自定义提示词

        Returns:
            (success, message, titles)
            titles 格式: [{"title": "...", "type": "...", "trigger": "..."}, ...]
        """
        try:
            # 构建系统提示词
            system_prompt = prompt_config.system_prompt

            # 构建用户消息
            user_message = f"""
请根据以下原始内容，生成5个爆款标题变体：

原始标题：{original_title}
原始描述：{original_desc}
原始标签：{', '.join(tags)}

{f"用户要求：{user_prompt}" if user_prompt else ""}

请按照以下格式输出（JSON）：
{{
  "titles": [
    {{
      "title": "标题内容",
      "type": "类型（数字冲击型/身份对比型/认知颠覆型/痛点放大型/秘密揭露型/紧迫警告型/反问共鸣型）",
      "trigger": "核心触发点（一句话说明为什么有效）"
    }},
    ...
  ]
}}
"""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=2048,
                temperature=0.8,  # 稍高的温度增加创意
            )

            content = response.choices[0].message.content

            # 解析 JSON
            # 尝试提取 JSON 块
            json_str = content
            if "```json" in content:
                json_str = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                json_str = content.split("```")[1].split("```")[0]

            result = json.loads(json_str.strip())
            titles = result.get("titles", [])

            logger.info(f"生成 {len(titles)} 个标题变体")
            return True, "成功", titles

        except json.JSONDecodeError as e:
            error_msg = f"解析标题JSON失败: {str(e)}"
            logger.error(error_msg)
            # 返回原始内容作为备选
            return True, "使用原始标题", [{"title": original_title, "type": "原始", "trigger": "保留原样"}]

        except Exception as e:
            error_msg = f"生成标题失败: {str(e)}"
            logger.error(error_msg)
            return False, error_msg, None

    def rewrite_content(
        self,
        original_title: str,
        original_desc: str,
        tags: list[str],
        user_prompt: Optional[str] = None
    ) -> tuple[bool, str, Optional[str]]:
        """
        改写正文内容

        Args:
            original_title: 原始标题
            original_desc: 原始描述
            tags: 标签列表
            user_prompt: 用户自定义提示词

        Returns:
            (success, message, new_content)
        """
        try:
            system_prompt = prompt_config.content_prompt

            user_message = f"""
请改写以下小红书笔记内容：

原始标题：{original_title}
原始描述：{original_desc}
原始标签：{', '.join(tags)}

{f"用户要求：{user_prompt}" if user_prompt else ""}

要求：
1. 保持原意，但用不同的表达方式
2. 增加情感色彩
3. 适当使用 emoji
4. 保留原标签，放在文末
5. 字数控制在 150-300 字

直接输出改写后的内容，不需要其他说明。
"""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=1024,
                temperature=0.7,
            )

            new_content = response.choices[0].message.content
            logger.info(f"文案改写成功，字数: {len(new_content)}")
            return True, "成功", new_content

        except Exception as e:
            error_msg = f"文案改写失败: {str(e)}"
            logger.error(error_msg)
            return False, error_msg, None

    def generate_image_prompt(
        self,
        image_descriptions: list[str],
        style: Optional[str] = None
    ) -> tuple[bool, str, Optional[str]]:
        """
        根据图片描述生成图片生成提示词

        Args:
            image_descriptions: 图片描述列表
            style: 指定风格

        Returns:
            (success, message, prompt)
        """
        try:
            base_style = style or prompt_config.image_style

            user_message = f"""
请根据以下图片描述，生成一个适合 AI 绘画的提示词。

图片描述：
{chr(10).join(f'{i+1}. {desc}' for i, desc in enumerate(image_descriptions))}

风格要求：
{base_style}

要求：
1. 提取图片的核心视觉元素
2. 结合风格描述，生成连贯的提示词
3. 使用中文描述，因为图片生成模型支持中文
4. 适合 3:4 竖版图片
5. 不要在图片中生成文字内容，只描述视觉风格和元素

直接输出提示词，不需要其他说明。
"""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": user_message}
                ],
                max_tokens=512,
                temperature=0.5,
            )

            prompt = response.choices[0].message.content.strip()
            logger.info(f"生成图片提示词成功: {prompt[:100]}...")
            return True, "成功", prompt

        except Exception as e:
            error_msg = f"生成图片提示词失败: {str(e)}"
            logger.error(error_msg)
            return False, error_msg, None


# 全局实例
llm_service = LLMService()
