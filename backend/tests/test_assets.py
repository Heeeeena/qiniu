import sys
from pathlib import Path

from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.main import app  # noqa: E402
from app.schemas.assets import GenerateRequest  # noqa: E402
from app.services.prompt_builder import build_prompt  # noqa: E402


def test_prompt_builder_adds_game_asset_constraints() -> None:
    request = GenerateRequest(
        project_name="Demo",
        description="蓝色魔法水晶",
        asset_type="item",
        style="pixel",
        size=128,
        count=2,
        transparent_background=True,
        palette="ocean",
        consistency_seed="demo-seed",
        style_pack_name="Dungeon Pixel Pack",
        target_engine="unity",
        naming_prefix="demo_item",
    )

    prompt, constraints = build_prompt(request)

    assert "2D game item icon" in prompt
    assert "style pack: Dungeon Pixel Pack" in prompt
    assert "naming prefix: demo_item" in prompt
    assert "Unity/Godot/Cocos import-ready" in prompt
    assert "transparent background" in prompt
    assert "128x128px" in prompt
    assert "type:item" in constraints
    assert "pack:Dungeon Pixel Pack" in constraints
    assert "engine:unity" in constraints
    assert "prefix:demo_item" in constraints
    assert "seed:demo-seed" in constraints


def test_generate_assets_endpoint_returns_png_data_urls() -> None:
    client = TestClient(app)

    response = client.post(
        "/api/assets/generate",
        json={
            "project_name": "Demo",
            "description": "蓝色魔法水晶",
            "asset_type": "item",
            "style": "pixel",
            "size": 128,
            "count": 2,
            "transparent_background": True,
            "palette": "ocean",
            "consistency_seed": "demo-seed",
            "style_pack_name": "Dungeon Pixel Pack",
            "target_engine": "unity",
            "naming_prefix": "demo_item",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["enhanced_prompt"]
    assert payload["quality_checks"]
    assert len(payload["assets"]) == 2
    assert payload["assets"][0]["data_url"].startswith("data:image/png;base64,")
    assert payload["assets"][0]["metadata"]["generator"] == "local-pillow"
    assert payload["assets"][0]["metadata"]["style_pack_name"] == "Dungeon Pixel Pack"
    assert payload["assets"][0]["metadata"]["target_engine"] == "unity"
    assert payload["assets"][0]["metadata"]["naming_prefix"] == "demo_item"

    quality_by_key = {check["key"]: check for check in payload["quality_checks"]}
    assert quality_by_key["dimension"]["status"] == "pass"
    assert quality_by_key["metadata"]["status"] == "pass"
    assert quality_by_key["engine_export"]["status"] == "pass"
    assert quality_by_key["naming"]["status"] == "pass"
    assert quality_by_key["style_consistency"]["status"] == "pass"
