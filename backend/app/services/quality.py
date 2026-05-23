from __future__ import annotations

import base64
import io

from PIL import Image

from app.schemas.assets import GenerateRequest, GeneratedAsset, QualityCheck


def inspect_assets(request: GenerateRequest, assets: list[GeneratedAsset]) -> list[QualityCheck]:
    images = [_decode_image(asset.data_url) for asset in assets]
    sizes = [image.size for image in images]
    expected_size = (request.size, request.size)
    required_metadata = {
        "project_name",
        "style_pack_name",
        "target_engine",
        "naming_prefix",
        "source_description",
        "palette",
        "transparent_background",
        "generator",
        "variant",
    }

    checks = [
        QualityCheck(
            key="batch_count",
            label="批量数量",
            status="pass" if len(assets) == request.count else "fail",
            detail=f"期望 {request.count} 张，实际 {len(assets)} 张。",
        ),
        QualityCheck(
            key="dimension",
            label="尺寸规范",
            status="pass" if sizes and all(size == expected_size for size in sizes) else "fail",
            detail=f"目标尺寸 {request.size}x{request.size}px，检测到 {sorted(set(sizes)) or '无素材'}。",
        ),
        QualityCheck(
            key="alpha_channel",
            label="透明通道",
            status=_alpha_status(request, images),
            detail=_alpha_detail(request, images),
        ),
        QualityCheck(
            key="metadata",
            label="元数据",
            status="pass"
            if all(required_metadata.issubset(set(asset.metadata.keys())) for asset in assets)
            else "fail",
            detail="导出包可追溯项目、风格包、色板、Prompt、seed 和生成器。",
        ),
        QualityCheck(
            key="spritesheet",
            label="Sprite Sheet",
            status="pass" if assets and len(set(sizes)) == 1 and len(assets) <= 8 else "warn",
            detail="当前批次可按统一网格拼接，适合导入 Unity、Godot、Cocos 或 Aseprite。",
        ),
        QualityCheck(
            key="engine_export",
            label="引擎导出",
            status="pass" if request.target_engine in {"unity", "godot", "cocos", "tiled", "aseprite"} else "warn",
            detail=f"当前导出目标为 {request.target_engine}，ZIP 将包含对应导入说明和 Sprite Sheet manifest。",
        ),
        QualityCheck(
            key="naming",
            label="命名规范",
            status="pass" if request.naming_prefix else "warn",
            detail="建议设置批次命名前缀，便于引擎资源检索、版本管理和 Sprite Sheet 帧名映射。",
        ),
        QualityCheck(
            key="style_consistency",
            label="风格一致性",
            status="pass" if _metadata_matches_request(request, assets) else "warn",
            detail="素材共享同一风格、色板、尺寸和一致性种子。",
        ),
    ]

    if request.asset_type == "tile":
        checks.append(
            QualityCheck(
                key="tile_grid",
                label="瓦片网格",
                status="pass" if request.size in {32, 64, 128, 256, 512} else "fail",
                detail="瓦片尺寸为 2 的幂，便于接入 TileMap 和 Tile Palette。",
            )
        )

    return checks


def _decode_image(data_url: str) -> Image.Image:
    _, encoded = data_url.split(",", 1)
    data = base64.b64decode(encoded)
    return Image.open(io.BytesIO(data)).convert("RGBA")


def _alpha_status(request: GenerateRequest, images: list[Image.Image]) -> str:
    if not images:
        return "fail"
    if not request.transparent_background:
        return "pass"
    return "pass" if all(image.mode == "RGBA" for image in images) else "fail"


def _alpha_detail(request: GenerateRequest, images: list[Image.Image]) -> str:
    if not images:
        return "未检测到图片。"
    if request.transparent_background:
        return "PNG 包含 Alpha 通道，可用于角色、道具、UI 和图标叠加。"
    return "当前素材使用展示背景，适合背景图或展示稿。"


def _metadata_matches_request(request: GenerateRequest, assets: list[GeneratedAsset]) -> bool:
    if not assets:
        return False
    return all(
        asset.style == request.style
        and asset.size == request.size
        and asset.seed.startswith(request.consistency_seed)
        and asset.metadata.get("palette") == request.palette
        and asset.metadata.get("style_pack_name") == (request.style_pack_name or "")
        and asset.metadata.get("target_engine") == request.target_engine
        and asset.metadata.get("naming_prefix") == (request.naming_prefix or "")
        for asset in assets
    )
