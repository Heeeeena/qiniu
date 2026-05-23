from typing import Literal

from pydantic import BaseModel, Field, field_validator


AssetType = Literal["character", "item", "tile", "background", "ui"]
AssetStyle = Literal["pixel", "cartoon", "ink", "dark", "sci-fi"]
PaletteName = Literal["ember", "forest", "ocean", "candy", "mono"]
QualityStatus = Literal["pass", "warn", "fail"]


class GenerateRequest(BaseModel):
    project_name: str = Field(default="Untitled Game", min_length=1, max_length=80)
    description: str = Field(min_length=1, max_length=500)
    asset_type: AssetType = "item"
    style: AssetStyle = "pixel"
    size: int = Field(default=128, ge=32, le=512)
    count: int = Field(default=4, ge=1, le=8)
    transparent_background: bool = True
    palette: PaletteName = "ocean"
    consistency_seed: str = Field(default="default", min_length=1, max_length=80)
    style_pack_name: str | None = Field(default=None, max_length=80)

    @field_validator("size")
    @classmethod
    def size_must_be_power_of_two(cls, value: int) -> int:
        if value not in {32, 64, 128, 256, 512}:
            raise ValueError("size must be one of 32, 64, 128, 256, 512")
        return value

    @field_validator("project_name", "description", "consistency_seed")
    @classmethod
    def trim_text(cls, value: str) -> str:
        return value.strip()

    @field_validator("style_pack_name")
    @classmethod
    def trim_optional_text(cls, value: str | None) -> str | None:
        if value is None:
            return value
        trimmed = value.strip()
        return trimmed or None


class GeneratedAsset(BaseModel):
    id: str
    name: str
    asset_type: AssetType
    style: AssetStyle
    size: int
    data_url: str
    seed: str
    prompt: str
    created_at: str
    metadata: dict[str, str | int | bool]


class QualityCheck(BaseModel):
    key: str
    label: str
    status: QualityStatus
    detail: str


class GenerateResponse(BaseModel):
    request_id: str
    enhanced_prompt: str
    constraints: list[str]
    quality_checks: list[QualityCheck]
    assets: list[GeneratedAsset]
