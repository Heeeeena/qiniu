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
    )

    prompt, constraints = build_prompt(request)

    assert "2D game item icon" in prompt
    assert "transparent background" in prompt
    assert "128x128px" in prompt
    assert "type:item" in constraints
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
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["enhanced_prompt"]
    assert len(payload["assets"]) == 2
    assert payload["assets"][0]["data_url"].startswith("data:image/png;base64,")
    assert payload["assets"][0]["metadata"]["generator"] == "local-pillow"
