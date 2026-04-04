"""
任务步骤函数 — 只做业务并返回结果，不碰数据库/WebSocket/异常兜底
"""
import asyncio
from pathlib import Path
from typing import Optional

from loguru import logger


async def fetch_note_step(crawler, url: str, selected_indices: list[int], cookies_plain: str = ""):
    """
    Phase 1: 爬取笔记内容

    Returns:
        note_data: NoteData 实例
    Raises:
        Exception: 爬取失败时抛出
    """
    success, msg, note_data = crawler.fetch_note(url, cookies=cookies_plain)
    if not success:
        raise Exception(f"获取笔记失败: {msg}")
    if not note_data:
        raise Exception("返回数据为空")

    # 根据选中的索引筛选图片
    all_images = note_data.images
    selected_images = [all_images[i] for i in selected_indices if i < len(all_images)]

    return note_data, selected_images


async def analyze_images_step(
    crawler, vision_service, images: list[str], save_dir: Path, vision_model: str
) -> tuple[list[Path], list[str]]:
    """
    Phase 2: 下载图片并分析

    Returns:
        (local_paths, descriptions)
    Raises:
        Exception: 下载或分析失败时抛出
    """
    # 下载图片到本地
    local_images = crawler.download_images(images, save_dir)
    if not local_images:
        raise Exception("图片下载失败，无可用图片")

    # 逐张分析
    descriptions = []
    for img_path in local_images:
        success, msg, desc = vision_service.analyze_image(img_path, model=vision_model)
        if not success:
            raise Exception(f"图片分析失败: {msg}")
        if desc:
            descriptions.append(desc)

    return local_images, descriptions


async def rewrite_content_step(
    llm_service, title: str, desc: str, tags: list[str], user_prompt: str = ""
) -> tuple[list[dict], str]:
    """
    Phase 3: 生成标题 + 改写文案

    Returns:
        (titles, new_content) — titles 是 list[dict]，new_content 是 str
    """
    # 生成标题
    success, _, titles = llm_service.generate_titles(title, desc, tags, user_prompt)
    if not success:
        raise Exception("标题生成失败")

    # 改写文案
    success, _, new_content = llm_service.rewrite_content(title, desc, tags, user_prompt)
    if not success:
        raise Exception("文案改写失败")

    return titles or [], new_content or desc


async def generate_images_step(
    image_gen_service,
    prompt: str,
    task_id: str,
    count: int,
    output_dir: Path,
    model: str = "nano-banana-2",
    ratio: str = "3:4",
) -> list[str]:
    """
    Phase 4: 并发生成图片

    Returns:
        generated_image_paths — 生成的本地图片路径列表
    """
    async def generate_single(index: int):
        save_path = output_dir / "images" / task_id / f"generated_{index}.png"
        success, _, img_path = await image_gen_service.generate_image(
            prompt, save_path, model=model, aspect_ratio=ratio
        )
        return (index, success, str(img_path) if success and img_path else None)

    results = await asyncio.gather(*[generate_single(i) for i in range(count)])

    generated = []
    for index, success, img_path in sorted(results):
        if success and img_path:
            generated.append(img_path)

    return generated


def save_result_step(task, output_dir: Path) -> None:
    """
    Phase 5: 保存文本结果到文件（同步函数，纯本地 IO）
    """
    save_dir = output_dir / "texts" / task.task_id
    save_dir.mkdir(parents=True, exist_ok=True)

    title_file = save_dir / "title.txt"
    title_file.write_text(task.generated_title or "", encoding="utf-8")

    content = f"{task.generated_title}\n\n{task.generated_desc}\n\n"
    if task.original_tags:
        tags_text = " ".join(f"#{tag}" for tag in task.original_tags)
        content += tags_text

    content_file = save_dir / "content.txt"
    content_file.write_text(content, encoding="utf-8")

    logger.info(f"文本结果已保存: {save_dir}")
