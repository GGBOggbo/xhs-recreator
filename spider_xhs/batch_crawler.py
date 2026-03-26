# -*- coding: utf-8 -*-
"""
小红书批量采集工具 - HTML解析版
- 从URL列表批量采集笔记数据
- 保存为Excel格式
- 下载无水印图片和视频
"""

import os
import re
import json
import time
import requests
import pandas as pd
from pathlib import Path
from urllib.parse import urlparse, parse_qs
from loguru import logger

# ==================== 配置区域 ====================

# Cookie（从小红书网页版获取，需要登录后的Cookie）
COOKIE = """a1=19b3ad142643514e3no3a156k813bnlqwxko0j9wh50000109313; webId=dea0d210ef349df5f8a0735fceabd924; gid=yjDq0fyj0qEyyjDq0fy4JCVjK4q2y4dqIlq0TExy2KTYyl28qDI1A8888y8jqyq848WffqSd; abRequestId=dea0d210ef349df5f8a0735fceabd924; webBuild=6.1.2; xsecappid=xhs-pc-web; websectiga=a9bdcaed0af874f3a1431e94fbea410e8f738542fbb02df1e8e30c29ef3d91ac; sec_poison_id=0a5117a8-3542-48f5-973c-4361f083edcc"""

# 笔记URL列表
NOTE_URLS = [
    "https://www.xiaohongshu.com/explore/69b6b450000000002301e76a?xsec_token=AB3XDcaUQ314o5MrXzzW3QRGSKMNlgOO5w6OElW54Frkg=&xsec_source=pc_feed",
    # 添加更多URL...
]

# 输出目录
OUTPUT_DIR = "./output"
MEDIA_DIR = "./output/media"

# 请求间隔（秒）
REQUEST_INTERVAL = 1.5

# ==================== 代码区域 ====================

class XHSCrawler:
    def __init__(self, cookie: str):
        self.cookie = cookie.strip()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Referer': 'https://www.xiaohongshu.com/',
            'Cookie': self.cookie
        })

    def get_note_from_html(self, url: str) -> dict:
        """从HTML页面解析笔记数据"""
        try:
            resp = self.session.get(url, timeout=30)
            resp.raise_for_status()

            # 提取 __INITIAL_STATE__
            match = re.search(r'window\.__INITIAL_STATE__\s*=\s*({.*?})\s*</script>', resp.text, re.DOTALL)
            if not match:
                logger.error("未找到 __INITIAL_STATE__")
                return None

            # 清理JSON字符串
            json_str = match.group(1)
            # 处理可能的undefined
            json_str = re.sub(r':\s*undefined', ': null', json_str)

            data = json.loads(json_str)

            # 提取笔记数据
            note_data = data.get('note', {}).get('noteDetailMap', {})
            if not note_data:
                logger.error("未找到笔记数据")
                return None

            # 获取第一个笔记
            note_id = list(note_data.keys())[0]
            note = note_data[note_id].get('note', {})

            return {
                'note_id': note.get('noteId', ''),
                'title': note.get('title', ''),
                'desc': note.get('desc', ''),
                'type': note.get('type', 'normal'),  # normal=图文, video=视频
                'time': note.get('time', ''),
                'user_id': note.get('user', {}).get('userId', ''),
                'user_name': note.get('user', {}).get('nickname', ''),
                'user_avatar': note.get('user', {}).get('avatar', ''),
                'liked_count': note.get('interactInfo', {}).get('likedCount', 0),
                'collected_count': note.get('interactInfo', {}).get('collectedCount', 0),
                'comment_count': note.get('interactInfo', {}).get('commentCount', 0),
                'share_count': note.get('interactInfo', {}).get('shareCount', 0),
                'cover_url': note.get('imageList', [{}])[0].get('urlDefault', '') if note.get('imageList') else '',
                'images': note.get('imageList', []),
                'video': note.get('video', {}),
                'topics': [t.get('name', '') for t in note.get('topics', [])],
                'tags': [t.get('name', '') for t in note.get('tagList', [])],
                'url': url
            }

        except Exception as e:
            logger.error(f"解析失败: {e}")
            return None

    def get_no_watermark_image_url(self, img_url: str) -> str:
        """获取无水印图片URL"""
        try:
            # https://sns-webpic-qc.xhscdn.com/202403211626/xxx/110/0/01e50c1c..._0.jpg!nd_dft_wlteh_webp_3
            if '.jpg' in img_url or 'webpic' in img_url:
                img_id = '/'.join(img_url.split('/')[-3:]).split('!')[0]
                return f'https://sns-img-qc.xhscdn.com/{img_id}'
            elif 'spectrum' in img_url:
                img_id = '/'.join(img_url.split('/')[-2:]).split('!')[0]
                return f'http://sns-webpic.xhscdn.com/{img_id}?imageView2/2/w/format/jpg'
            else:
                img_id = img_url.split('/')[-1].split('!')[0]
                return f'https://sns-img-qc.xhscdn.com/{img_id}'
        except:
            return img_url

    def download_file(self, url: str, save_path: str) -> bool:
        """下载文件"""
        try:
            resp = self.session.get(url, timeout=60, stream=True)
            resp.raise_for_status()

            with open(save_path, 'wb') as f:
                for chunk in resp.iter_content(chunk_size=8192):
                    f.write(chunk)
            return True
        except Exception as e:
            logger.error(f"下载失败: {e}")
            return False


def main():
    # 创建输出目录
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(MEDIA_DIR, exist_ok=True)

    if not NOTE_URLS:
        logger.error("请先在 NOTE_URLS 中添加要采集的笔记URL！")
        return

    crawler = XHSCrawler(COOKIE)
    results = []
    media_files = []

    logger.info(f"开始采集，共 {len(NOTE_URLS)} 个URL")
    logger.info("=" * 50)

    for i, url in enumerate(NOTE_URLS):
        logger.info(f"[{i+1}/{len(NOTE_URLS)}] 采集: {url}")

        # 获取笔记数据
        note = crawler.get_note_from_html(url)
        if not note:
            logger.error("  获取失败")
            continue

        logger.info(f"  标题: {note['title']}")
        logger.info(f"  作者: {note['user_name']}")
        logger.info(f"  点赞: {note['liked_count']} | 收藏: {note['collected_count']}")

        images_downloaded = 0
        video_downloaded = False

        # 下载图片
        for j, img in enumerate(note['images']):
            # 优先使用 urlPre，其次 infoList
            img_url = img.get('urlPre', '')
            if not img_url and img.get('infoList'):
                # 获取最高清的图片
                for info in img.get('infoList', []):
                    if info.get('url'):
                        img_url = info['url']
                        break

            if not img_url:
                continue

            # 直接下载（原始URL已是无水印）
            save_path = os.path.join(MEDIA_DIR, f"{note['note_id']}_img_{j}.jpg")

            if crawler.download_file(img_url, save_path):
                images_downloaded += 1
                logger.info(f"  下载图片 {j+1}: {save_path}")

        # 下载视频
        if note['video']:
            video_url = note['video'].get('media', {}).get('stream', {}).get('h264', [{}])
            if video_url:
                video_url = video_url[0].get('masterUrl', '')
                if video_url:
                    save_path = os.path.join(MEDIA_DIR, f"{note['note_id']}_video.mp4")
                    if crawler.download_file(video_url, save_path):
                        video_downloaded = True
                        logger.info(f"  下载视频: {save_path}")

        # 整理数据
        results.append({
            'note_id': note['note_id'],
            'title': note['title'],
            'desc': note['desc'],
            'topics': ', '.join(note['topics']),
            'tags': ', '.join(note['tags']),
            'author': note['user_name'],
            'author_id': note['user_id'],
            'likes': note['liked_count'],
            'collects': note['collected_count'],
            'comments': note['comment_count'],
            'shares': note['share_count'],
            'type': '视频' if note['video'] else '图文',
            'images': len(note['images']),
            'images_downloaded': images_downloaded,
            'video_downloaded': '是' if video_downloaded else '否',
            'time': note['time'],
            'url': url
        })

        logger.info(f"  ✓ 完成")

        # 请求间隔
        if i < len(NOTE_URLS) - 1:
            time.sleep(REQUEST_INTERVAL)

    # 保存Excel
    if results:
        df = pd.DataFrame(results)
        excel_path = os.path.join(OUTPUT_DIR, "notes.xlsx")
        df.to_excel(excel_path, index=False, engine='openpyxl')

        logger.info("=" * 50)
        logger.info(f"采集完成!")
        logger.info(f"  - 成功采集: {len(results)} 条笔记")
        logger.info(f"  - Excel: {excel_path}")
        logger.info(f"  - 媒体目录: {MEDIA_DIR}")
    else:
        logger.warning("没有采集到任何数据")


if __name__ == "__main__":
    main()
