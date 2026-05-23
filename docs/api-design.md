# API 设计

## GET `/api/health`

返回服务状态。

```json
{
  "status": "ok",
  "generator": "local"
}
```

## POST `/api/assets/generate`

生成一批 2D 游戏素材。

### Request

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
  "consistency_seed": "qiniu-first-batch"
}
```

### Response

```json
{
  "request_id": "uuid",
  "enhanced_prompt": "enhanced prompt",
  "constraints": ["type:item", "style:pixel", "size:128px"],
  "assets": [
    {
      "id": "asset-id",
      "name": "item-01",
      "asset_type": "item",
      "style": "pixel",
      "size": 128,
      "data_url": "data:image/png;base64,...",
      "seed": "qiniu-first-batch-item-1",
      "prompt": "enhanced prompt",
      "created_at": "2026-05-23T00:00:00+00:00",
      "metadata": {
        "project_name": "Dungeon Starter Kit",
        "palette": "ocean",
        "generator": "local-pillow"
      }
    }
  ]
}
```

## 后续扩展

- `POST /api/assets/upscale`：素材放大。
- `POST /api/assets/remove-background`：背景移除。
- `POST /api/assets/export/spritesheet`：服务端 Sprite Sheet。
- `POST /api/projects`：项目级风格包持久化。
