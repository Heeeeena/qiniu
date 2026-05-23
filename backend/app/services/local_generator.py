from __future__ import annotations

import base64
import hashlib
import io
import random
import uuid
from datetime import UTC, datetime

from PIL import Image, ImageDraw, ImageFilter

from app.schemas.assets import GenerateRequest, GeneratedAsset


PALETTES: dict[str, list[str]] = {
    "ember": ["#151515", "#f2552c", "#ffb238", "#f7f1d7"],
    "forest": ["#163a2f", "#2f8f5b", "#92c96a", "#f4e7ba"],
    "ocean": ["#102542", "#1f7a8c", "#7dcfb6", "#f2f7f2"],
    "candy": ["#2b2d42", "#ff5d8f", "#ffc8dd", "#f8f7ff"],
    "mono": ["#121212", "#555555", "#aaaaaa", "#f5f5f5"],
}


class LocalAssetGenerator:
    def generate(self, request: GenerateRequest, prompt: str) -> list[GeneratedAsset]:
        assets: list[GeneratedAsset] = []
        request_id = hashlib.sha1(f"{request.consistency_seed}:{request.description}".encode()).hexdigest()[:8]

        for index in range(request.count):
            seed = f"{request.consistency_seed}-{request.asset_type}-{index + 1}"
            image = self._render(request, seed)
            data_url = self._to_data_url(image)
            asset_name = f"{request.asset_type}-{index + 1:02d}"
            assets.append(
                GeneratedAsset(
                    id=f"{request_id}-{index + 1}",
                    name=asset_name,
                    asset_type=request.asset_type,
                    style=request.style,
                    size=request.size,
                    data_url=data_url,
                    seed=seed,
                    prompt=prompt,
                    created_at=datetime.now(UTC).isoformat(),
                    metadata={
                        "project_name": request.project_name,
                        "style_pack_name": request.style_pack_name or "",
                        "target_engine": request.target_engine,
                        "naming_prefix": request.naming_prefix or "",
                        "source_description": request.description,
                        "palette": request.palette,
                        "transparent_background": request.transparent_background,
                        "generator": "local-pillow",
                        "variant": index + 1,
                    },
                )
            )

        return assets

    def _render(self, request: GenerateRequest, seed: str) -> Image.Image:
        rng = self._rng(seed)
        draw_size = 64 if request.style == "pixel" and request.size > 64 else request.size
        image = self._blank(draw_size, request.transparent_background, request.palette, rng)
        draw = ImageDraw.Draw(image, "RGBA")

        if request.asset_type == "character":
            self._draw_character(draw, draw_size, request.palette, rng)
        elif request.asset_type == "tile":
            self._draw_tile(draw, draw_size, request.palette, rng)
        elif request.asset_type == "background":
            self._draw_background(draw, draw_size, request.palette, rng)
        elif request.asset_type == "ui":
            self._draw_ui(draw, draw_size, request.palette, rng)
        else:
            self._draw_item(draw, draw_size, request.palette, rng)

        self._apply_style(image, draw, request.style, request.palette, rng)

        if draw_size != request.size:
            image = image.resize((request.size, request.size), Image.Resampling.NEAREST)

        return image

    def _blank(self, size: int, transparent: bool, palette_name: str, rng: random.Random) -> Image.Image:
        if transparent:
            return Image.new("RGBA", (size, size), (0, 0, 0, 0))

        colors = PALETTES[palette_name]
        base = Image.new("RGBA", (size, size), colors[3])
        draw = ImageDraw.Draw(base, "RGBA")
        for _ in range(18):
            x = rng.randint(0, size)
            y = rng.randint(0, size)
            radius = rng.randint(size // 12, size // 4)
            draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=self._hex_to_rgba(colors[2], 34))
        return base

    def _draw_item(self, draw: ImageDraw.ImageDraw, size: int, palette_name: str, rng: random.Random) -> None:
        colors = PALETTES[palette_name]
        cx = cy = size // 2
        radius = int(size * 0.26)
        if rng.random() > 0.5:
            points = [
                (cx, cy - radius - 10),
                (cx + radius, cy - 6),
                (cx + int(radius * 0.58), cy + radius),
                (cx - int(radius * 0.58), cy + radius),
                (cx - radius, cy - 6),
            ]
            draw.polygon(points, fill=colors[2], outline=colors[0])
            draw.line((cx, cy - radius - 8, cx, cy + radius), fill=self._hex_to_rgba(colors[3], 140), width=max(1, size // 42))
        else:
            draw.rounded_rectangle(
                (cx - radius, cy - radius, cx + radius, cy + radius),
                radius=max(4, size // 10),
                fill=colors[1],
                outline=colors[0],
                width=max(2, size // 36),
            )
            draw.ellipse(
                (cx - radius // 2, cy - radius // 2, cx + radius // 2, cy + radius // 2),
                fill=colors[2],
                outline=colors[3],
            )
        draw.ellipse((cx - 5, cy - radius, cx + 9, cy - radius + 14), fill=self._hex_to_rgba(colors[3], 130))

    def _draw_character(self, draw: ImageDraw.ImageDraw, size: int, palette_name: str, rng: random.Random) -> None:
        colors = PALETTES[palette_name]
        cx = size // 2
        head = int(size * 0.18)
        body_top = int(size * 0.42)
        draw.ellipse((cx - head, int(size * 0.18), cx + head, int(size * 0.18) + head * 2), fill=colors[3], outline=colors[0], width=max(2, size // 40))
        draw.rounded_rectangle((cx - head, body_top, cx + head, int(size * 0.76)), radius=max(4, size // 12), fill=colors[1], outline=colors[0], width=max(2, size // 38))
        draw.rectangle((cx - head - 10, body_top + 6, cx - head, int(size * 0.66)), fill=colors[2])
        draw.rectangle((cx + head, body_top + 6, cx + head + 10, int(size * 0.66)), fill=colors[2])
        eye_y = int(size * 0.28)
        draw.rectangle((cx - 9, eye_y, cx - 5, eye_y + 4), fill=colors[0])
        draw.rectangle((cx + 5, eye_y, cx + 9, eye_y + 4), fill=colors[0])
        if rng.random() > 0.45:
            draw.line((cx + head + 8, body_top, cx + head + 26, int(size * 0.23)), fill=colors[2], width=max(2, size // 30))
            draw.polygon([(cx + head + 25, int(size * 0.2)), (cx + head + 35, int(size * 0.12)), (cx + head + 31, int(size * 0.24))], fill=colors[3], outline=colors[0])

    def _draw_tile(self, draw: ImageDraw.ImageDraw, size: int, palette_name: str, rng: random.Random) -> None:
        colors = PALETTES[palette_name]
        tile = max(8, size // 4)
        draw.rectangle((0, 0, size, size), fill=colors[1])
        for y in range(0, size, tile):
            for x in range(0, size, tile):
                inset = rng.randint(1, max(2, tile // 8))
                draw.rectangle((x + inset, y + inset, x + tile - inset, y + tile - inset), fill=self._hex_to_rgba(colors[2], 150), outline=self._hex_to_rgba(colors[0], 120))
                if rng.random() > 0.68:
                    draw.line((x + 3, y + tile - 4, x + tile - 5, y + 5), fill=self._hex_to_rgba(colors[0], 130), width=1)
        draw.rectangle((0, 0, size - 1, size - 1), outline=colors[0], width=max(1, size // 48))

    def _draw_background(self, draw: ImageDraw.ImageDraw, size: int, palette_name: str, rng: random.Random) -> None:
        colors = PALETTES[palette_name]
        draw.rectangle((0, 0, size, size), fill=colors[0])
        for y in range(size):
            alpha = int(180 * y / size)
            draw.line((0, y, size, y), fill=self._hex_to_rgba(colors[1], alpha))
        for layer in range(3):
            base_y = int(size * (0.48 + layer * 0.15))
            points = [(0, size)]
            for x in range(0, size + 1, max(8, size // 7)):
                points.append((x, base_y + rng.randint(-size // 10, size // 9)))
            points.append((size, size))
            draw.polygon(points, fill=self._hex_to_rgba(colors[layer % 3], 210 - layer * 35))
        for _ in range(10):
            x = rng.randint(4, size - 4)
            y = rng.randint(4, max(6, size // 2))
            draw.ellipse((x - 1, y - 1, x + 1, y + 1), fill=colors[3])

    def _draw_ui(self, draw: ImageDraw.ImageDraw, size: int, palette_name: str, rng: random.Random) -> None:
        colors = PALETTES[palette_name]
        pad = int(size * 0.14)
        draw.rounded_rectangle((pad, pad, size - pad, size - pad), radius=max(5, size // 10), fill=self._hex_to_rgba(colors[3], 235), outline=colors[0], width=max(2, size // 34))
        draw.rounded_rectangle((pad * 2, int(size * 0.42), size - pad * 2, int(size * 0.64)), radius=max(4, size // 14), fill=colors[1], outline=colors[0], width=max(1, size // 48))
        if rng.random() > 0.35:
            draw.polygon(
                [
                    (int(size * 0.47), int(size * 0.47)),
                    (int(size * 0.47), int(size * 0.59)),
                    (int(size * 0.58), int(size * 0.53)),
                ],
                fill=colors[3],
            )
        draw.line((pad * 2, int(size * 0.32), size - pad * 2, int(size * 0.32)), fill=self._hex_to_rgba(colors[2], 190), width=max(2, size // 36))

    def _apply_style(self, image: Image.Image, draw: ImageDraw.ImageDraw, style: str, palette_name: str, rng: random.Random) -> None:
        colors = PALETTES[palette_name]
        size = image.size[0]
        if style == "ink":
            for _ in range(7):
                y = rng.randint(0, size)
                draw.arc((rng.randint(-10, 10), y - 20, size + rng.randint(-10, 10), y + 20), 180, 360, fill=self._hex_to_rgba(colors[0], 80), width=1)
        elif style == "dark":
            overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
            overlay_draw = ImageDraw.Draw(overlay)
            overlay_draw.rectangle((0, 0, size, size), fill=(0, 0, 0, 38))
            image.alpha_composite(overlay)
        elif style == "sci-fi":
            for _ in range(4):
                x = rng.randint(size // 6, size - size // 6)
                draw.line((x, size // 5, x, size - size // 5), fill=self._hex_to_rgba(colors[2], 100), width=1)
        elif style == "cartoon":
            image.alpha_composite(image.filter(ImageFilter.GaussianBlur(radius=0.2)))

    def _rng(self, seed: str) -> random.Random:
        digest = hashlib.sha256(seed.encode("utf-8")).hexdigest()
        return random.Random(int(digest[:16], 16))

    def _to_data_url(self, image: Image.Image) -> str:
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        encoded = base64.b64encode(buffer.getvalue()).decode("ascii")
        return f"data:image/png;base64,{encoded}"

    def _hex_to_rgba(self, color: str, alpha: int) -> tuple[int, int, int, int]:
        color = color.lstrip("#")
        return tuple(int(color[index : index + 2], 16) for index in (0, 2, 4)) + (alpha,)


local_generator = LocalAssetGenerator()
