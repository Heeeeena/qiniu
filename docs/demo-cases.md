# Demo Cases

录制 Demo 或评委本地体验时，推荐直接使用前端左侧的示例场景。

## 1. Dungeon Pixel Pack

- 项目：Dungeon Starter Kit
- 素材需求：一套地牢探索游戏里的蓝色魔法水晶、入口石门和发光地砖
- 素材类型：道具
- 风格：像素
- 色板：Ocean
- 目标引擎：Unity
- 命名前缀：`dungeon_pixel`
- 推荐展示点：
  - 风格包复用
  - 透明背景
  - ZIP 导出
  - Unity 导入说明

## 2. Forest Cartoon Kit

- 项目：Forest Adventure Kit
- 素材需求：一组森林冒险游戏的主角、蘑菇护符、叶片徽章和治疗果实
- 素材类型：角色
- 风格：卡通
- 色板：Forest
- 目标引擎：Godot
- 命名前缀：`forest_cartoon`
- 推荐展示点：
  - 同一色板和 seed 约束
  - 历史记录复用
  - Godot 导入说明

## 3. Sci-fi UI Kit

- 项目：Sci-fi HUD Kit
- 素材需求：一套科幻机甲游戏的能量按钮、状态面板、技能图标和警报徽章
- 素材类型：UI
- 风格：科幻
- 色板：Mono
- 目标引擎：Cocos
- 命名前缀：`scifi_ui`
- 推荐展示点：
  - UI 素材批量生成
  - Sprite Sheet manifest
  - Cocos 导入说明

## ZIP 检查点

导出的 ZIP 应包含：

```txt
images/
spritesheet/
  spritesheet.png
  spritesheet.json
metadata.json
engine-import-guide.md
README.md
```

`spritesheet.json` 中应能看到每一帧的 `x`、`y`、`width`、`height`、`sourceFile`、`seed`、`assetType` 和 `style`。
