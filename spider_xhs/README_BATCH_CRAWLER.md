# 小红书批量采集工具使用说明

## 快速开始

### 1. 获取Cookie

1. 浏览器打开 [小红书网页版](https://www.xiaohongshu.com) 并登录
2. 按 `F12` 打开开发者工具
3. 点击 **Network**（网络）标签
4. 刷新页面，在请求列表中点击任意一个请求
5. 在 **Headers** 中找到 `Cookie`，复制完整内容

### 2. 配置Cookie

编辑 `batch_crawler.py`，将 Cookie 粘贴到配置区域：

```python
COOKIE = """
a1=xxx; webId=xxx; ... （粘贴你的Cookie）
"""
```

### 3. 添加要采集的URL

在 `NOTE_URLS` 列表中添加笔记链接：

```python
NOTE_URLS = [
    "https://www.xiaohongshu.com/explore/64b95d01000000000c034587?xsec_token=AB0EFqJvINCkj6xOCKCQgfNNh8GdnBC_6XecG4QOddo3Q=&xsec_source=pc_search",
    # 添加更多URL...
]
```

**注意**：URL必须包含 `xsec_token` 参数，否则无法获取数据。

### 4. 运行采集

```bash
cd /root/Spider_XHS
python batch_crawler.py
```

## 输出结果

```
output/
├── notes.xlsx          # 笔记数据Excel
└── media/              # 媒体文件
    ├── {note_id}_img_0.jpg
    ├── {note_id}_img_1.jpg
    └── {note_id}_video.mp4
```

## Excel字段说明

| 列名 | 说明 |
|------|------|
| note_id | 笔记ID |
| title | 标题 |
| desc | 文案正文 |
| topics | 话题标签 |
| author_name | 作者昵称 |
| author_id | 作者ID |
| likes | 点赞数 |
| collects | 收藏数 |
| comments | 评论数 |
| share_count | 分享数 |
| type | 笔记类型(normal/video) |
| image_count | 图片数量 |
| has_video | 是否有视频 |
| images_downloaded | 已下载图片数 |
| video_downloaded | 是否下载视频 |
| time | 发布时间 |
| url | 原始链接 |

## 常见问题

### Q: 提示"请先配置Cookie"
**A:** 按照步骤1-2获取并配置Cookie

### Q: 采集失败，提示签名错误
**A:** Cookie可能已过期，重新获取并更新

### Q: URL中没有xsec_token怎么办？
**A:** 在小红书网页版打开笔记，从浏览器地址栏复制完整URL

### Q: 下载速度慢？
**A:** 这是正常的，为了避免触发风控，每次请求间隔1.5秒

## 注意事项

1. **仅供学习研究** - 请遵守平台规则，不得用于商业用途
2. **合理使用** - 控制采集频率，避免给平台造成负担
3. **Cookie有效期** - Cookie过期后需要重新获取
