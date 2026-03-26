# XHS ReCreator

小红书内容二创工具 - 通过 AI 自动改写文案并生成新图片

## 功能

- 输入小红书链接，自动爬取内容
- GLM-4.6V 多模态分析图片
- LLM 自动改写标题和文案
- NanoBanana2 生成新图片
- 输出小红书适配格式（3:4 竖版）

## 快速开始

### 1. 配置环境变量

```bash
cp backend/.env.example backend/.env
# 编辑 .env 填入你的 API Keys
```

### 2. 启动服务

```bash
docker-compose up -d --build
```

### 3. 访问

打开浏览器访问 http://localhost

## 配置

### 环境变量 (.env)

| 变量 | 说明 |
|------|------|
| ZHIPU_API_KEY | 智谱 AI API Key（GLM-4V 分析 + GLM-4 文案二创） |
| NANOBANANA_API_KEY | Nano Banana API Key（图片生成） |
| XHS_COOKIES | 小红书 Cookies（从浏览器开发者工具获取） |

### 提示词配置 (prompts.yaml)

可在 `backend/prompts.yaml` 中自定义：
- `system_prompt`: 标题二创系统提示词
- `content_prompt`: 正文改写提示词
- `vision_prompt`: 图片分析提示词
- `image_style`: 图片生成风格

## 目录结构

```
xhs_recreator/
├── backend/              # FastAPI 后端
│   ├── app/
│   │   ├── api/           # API 路由
│   │   ├── models/        # 数据模型
│   │   ├── services/      # 业务服务（爬虫、LLM、图片生成）
│   │   └── utils/         # 工具函数
│   ├── prompts.yaml       # 提示词配置
│   ├── requirements.txt
│   └── .env.example       # 环境变量模板
├── frontend/             # Vue 3 + Vite 前端
│   └── src/
│       ├── components/    # 页面组件
│       └── style.css
├── spider_xhs/            # 小红书爬虫模块
│   ├── apis/              # API 接口
│   ├── xhs_utils/        # 工具函数
│   └── static/            # 签名算法 JS
├── output/                # 输出文件
├── data/                  # SQLite 数据库
├── docker-compose.yml
├── Dockerfile.backend
├── Dockerfile.frontend
└── nginx.conf
```

## 致谢

- [Spider_XHS](https://github.com/cv-cat/Spider_XHS) - 小红书数据采集
- [智谱 AI](https://open.bigmodel.cn/) - GLM-4.6V 多模态分析 + GLM-4 文案二创
- [NanoBanana](https://grsai.dakka.com.cn) - AI 图片生成

## License

MIT
