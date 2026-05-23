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
  "consistency_seed": "qiniu-first-batch",
  "style_pack_name": "Dungeon Pixel Pack",
  "target_engine": "unity",
  "naming_prefix": "dungeon_pixel"
}
```

### Response

```json
{
  "request_id": "uuid",
  "enhanced_prompt": "enhanced prompt",
  "constraints": ["type:item", "style:pixel", "size:128px"],
  "quality_checks": [
    {
      "key": "dimension",
      "label": "尺寸规范",
      "status": "pass",
      "detail": "目标尺寸 128x128px，检测到 [(128, 128)]。"
    }
  ],
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
        "style_pack_name": "Dungeon Pixel Pack",
        "target_engine": "unity",
        "naming_prefix": "dungeon_pixel",
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
- `GET /api/style-packs`：服务端同步项目风格包。
- `POST /api/exports/engine-package`：服务端生成引擎导出包。
