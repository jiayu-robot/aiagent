# AI Daily Report Assistant

本项目是一个本地 Web 版“AI 日报生成助理”，面向现场工程师。第一版支持上传 Excel 日报模板、保存字段映射、输入中文工作记录、上传多张现场照片、生成可编辑中英文预览，并把确认后的内容和照片写入 Excel。

## 架构

- `app/api/`：FastAPI 接口，负责 HTTP 输入输出。
- `app/services/`：业务逻辑，包括模板、照片、语言处理、视觉分析、验证、Excel 生成和清理。
- `app/domain/`：Pydantic v2 数据模型，内部日报结构不依赖 Excel 模板。
- `app/providers/`：AI Provider 接口，默认使用 Fake Provider，真实 OpenAI Provider 可选。
- `data/persistent/`：永久数据，包括当前模板、profile 和术语表。
- `data/temporary/`：临时上传、压缩图、预览 JSON 和生成 Excel，超过 48 小时可清理。

## Windows 本地运行

```powershell
cd C:\Users\yangj\Desktop\daily-report-agent
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
fastapi dev app/main.py
```

访问：

```text
http://127.0.0.1:8000
```

## .env 配置

复制 `.env.example` 为 `.env`，默认 Fake Provider 不需要 API Key。

```env
APP_ENV=local
APP_DATA_ROOT=data
AI_PROVIDER=fake
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4.1-mini
MAX_EXCEL_BYTES=10485760
MAX_IMAGE_BYTES=10485760
TEMP_RETENTION_HOURS=48
```

## Fake Provider 模式

默认 `AI_PROVIDER=fake`。该模式输出确定性的中文润色、英文翻译和照片分类，便于本地测试，不调用外部网络或真实 AI API。

## 真实 AI Provider

设置：

```env
AI_PROVIDER=openai
OPENAI_API_KEY=你的_API_Key
OPENAI_MODEL=gpt-4.1-mini
```

API Key 只从环境变量读取，不写入日志和代码。

## 使用流程

1. 打开首页 `http://127.0.0.1:8000`。
2. 上传 `.xlsx` Excel 模板。
3. 打开 `/template` 保存字段映射。默认页面提供一份可编辑 JSON。
4. 回到首页，输入中文工作记录并上传照片。
5. 点击“AI 分析”进入预览页。
6. 在预览页编辑 JSON 后点击“生成 Excel”。
7. 浏览器会下载生成的日报文件。

## API

- `GET /health`
- `GET /api/templates/current`
- `POST /api/templates/upload`
- `POST /api/templates/profile`
- `GET /api/templates/inspect`
- `POST /api/reports/analyze`
- `GET /api/reports/{report_id}/preview`
- `POST /api/reports/{report_id}/generate`
- `GET /api/reports/{report_id}/download`

## 测试

```powershell
.\.venv\Scripts\python -m pytest -q
```

测试默认使用 Fake Provider，不调用真实 OpenAI API。

## Docker

```powershell
docker compose build
docker compose up -d
```

访问：

```text
http://localhost:8000
```

停止：

```powershell
docker compose down
```

Docker 使用官方 `python:3.12-slim` 多架构镜像，适合 Windows Docker Desktop，并为未来 Raspberry Pi 5 64-bit 迁移保留路径。

## 48 小时清理

```powershell
python scripts/cleanup.py
```

只清理：

- `data/temporary/jobs`
- `data/temporary/uploads`
- `data/temporary/processed_images`
- `data/temporary/outputs`

不会清理：

- `data/persistent/templates`
- `data/persistent/glossary`
- `.env`
- 源代码

## 常见错误

- `还没有上传当前 Excel 模板`：先上传 `.xlsx` 模板。
- `还没有保存模板字段映射`：打开 `/template` 保存 profile。
- `只支持图片文件`：照片只接受 JPG 或 PNG。
- `未配置 OPENAI_API_KEY`：真实 Provider 模式下需要 `.env` 配置 API Key。

## Raspberry Pi 迁移说明

未来迁移到 Raspberry Pi 5 64-bit 时，复制项目目录和 `data/persistent`，安装 Docker，再运行：

```powershell
docker compose up -d --build
```

当前版本不包含 Cloudflare Tunnel、公网认证、公司 SSO 或公网访问安全策略；如需公网使用，应先补认证和反向代理安全配置。
