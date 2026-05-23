# GameAssetForge

面向 2D 游戏开发者的素材生成与导出工作台。用户输入素材需求和简单参数后，系统生成统一风格的 PNG 素材，并支持导出 ZIP、Sprite Sheet 和 metadata.json，便于接入 Unity、Godot、Cocos、Tiled、Aseprite 等常见 2D 游戏开发流程。

## 选题

七牛云 x XEngineer 暑期实训营第一批次议题二：2D 游戏素材生成。

## 核心功能

- 参数化素材生成：支持角色、道具、瓦片、背景、UI 五类素材。
- 风格与色板约束：支持像素、卡通、手绘、暗黑、科幻风格，以及 Ember、Forest、Ocean、Candy、Mono 色板。
- 一致性种子：同一项目复用 seed，便于生成风格统一的素材包。
- 项目风格包：保存并复用素材类型、风格、色板、尺寸、透明背景和 seed，支持多套项目规范切换。
- Prompt 增强：后端将用户需求补全为更适合 2D 游戏素材生产的 Prompt。
- 质量检查：生成后自动检查尺寸、Alpha 通道、metadata、Sprite Sheet 适配和风格一致性。
- 游戏开发导出：支持单张 PNG、批量 ZIP、Sprite Sheet、metadata.json、Sprite Sheet manifest 和引擎导入说明。
- 引擎预设：支持 Unity、Godot、Cocos、Tiled、Aseprite 导出工作流。
- 批次命名规则：支持设置命名前缀，导出文件名和 Sprite Sheet 帧名保持一致。
- 历史记录：浏览器本地保存最近生成结果，可快速复用参数。

## 技术架构

```txt
frontend: Vue 3 + Vite + TypeScript + Pinia + Axios + JSZip
backend : Python + FastAPI + Pillow
env     : Conda environment.yml
```

当前版本使用本地 Pillow 生成器保证 Demo 可稳定运行。后续可在 `backend/app/services` 下替换为 OpenAI、Stable Diffusion、通义万相、火山方舟等图像生成服务。

## 本地启动

### 1. 安装前端依赖

```bash
cd frontend
npm install
npm run dev
```

前端默认运行在 `http://127.0.0.1:5173`。

### 2. 创建 Conda 环境

```bash
conda env create -f environment.yml
conda activate qiniu-assetforge
```

也可以在项目内创建环境：

```bash
conda env create -p ./.conda -f environment.yml
conda activate ./.conda
```

### 3. 启动后端

```bash
cd backend
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

后端健康检查：`http://127.0.0.1:8000/api/health`。

## 测试与验证

```bash
npm --prefix frontend run build
./.conda/python.exe -m compileall backend/app
./.conda/python.exe -m pytest backend/tests -q
```

Windows PowerShell 下也可以使用：

```powershell
.\.conda\python.exe -m pytest backend\tests -q
```

## API

### POST `/api/assets/generate`

请求示例：

```json
{
  "project_name": "Dungeon Starter Kit",
  "description": "一套地牢探索游戏里的蓝色魔法水晶、入口石门和发光地砖",
  "asset_type": "item",
  "style": "pixel",
  "size": 128,
  "count": 4,
  "transparent_background": true,
  "palette": "ocean",
  "consistency_seed": "qiniu-first-batch",
  "style_pack_name": "Dungeon Pixel Pack",
  "target_engine": "unity",
  "naming_prefix": "dungeon_pixel"
}
```

响应包含增强 Prompt、约束标签、质量检查结果和 PNG Data URL。

质量检查示例：

```json
{
  "key": "spritesheet",
  "label": "Sprite Sheet",
  "status": "pass",
  "detail": "当前批次可按统一网格拼接，适合导入 Unity、Godot、Cocos 或 Aseprite。"
}
```

## 导出格式

- `PNG`：单张素材，可直接导入游戏引擎。
- `ZIP`：包含 `/images`、`/spritesheet`、`metadata.json`、`engine-import-guide.md` 和导入说明。
- `Sprite Sheet`：将当前批次素材拼接成统一网格图。
- `spritesheet.json`：记录每帧素材在 Sprite Sheet 中的 `x`、`y`、`width`、`height`、原文件名、seed 和素材类型。
- `metadata.json`：记录素材类型、风格、尺寸、Prompt、seed 和生成时间。
- `qualityChecks`：记录尺寸、透明通道、metadata、Sprite Sheet 和风格一致性检查结果。

## 目录结构

```txt
qiniu/
  frontend/               # Vue 工作台
  backend/                # FastAPI 服务
    app/api/              # HTTP 接口
    app/schemas/          # Pydantic 数据模型
    app/services/         # Prompt 与生成服务
  docs/                   # 产品、API、Demo 文档
  samples/mock-assets/    # 示例素材说明
  environment.yml         # Conda 环境
```

## 第三方依赖

- Vue、Vite、TypeScript、Pinia、Axios、JSZip、FileSaver、Lucide Icons
- FastAPI、Uvicorn、Pillow、Pydantic Settings

## 原创说明

本仓库代码为本次议题从零构建。当前图片生成器为本地程序化生成方案，用于稳定演示完整产品闭环；真实模型接入点已在后端服务层预留。

## Demo 视频

待补充：提交前将 Demo 视频链接放置在此处。
