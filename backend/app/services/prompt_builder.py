from app.schemas.assets import GenerateRequest


ASSET_HINTS = {
    "character": "single 2D game character sprite, centered pose, readable silhouette",
    "item": "single 2D game item icon, centered object, clean contour",
    "tile": "seamless 2D tile texture, top-down game map material",
    "background": "2D side-scrolling game background layer, clear depth",
    "ui": "2D game UI panel or button, production-ready interface element",
}

STYLE_HINTS = {
    "pixel": "pixel art, crisp edges, limited colors, no blur",
    "cartoon": "cartoon style, bold shapes, friendly contrast",
    "ink": "hand-drawn ink style, expressive outline, subtle paper feel",
    "dark": "dark fantasy style, dramatic contrast, restrained highlights",
    "sci-fi": "sci-fi style, luminous accents, clean hard-surface details",
}

PALETTE_HINTS = {
    "ember": "charcoal, flame orange, warm gold, parchment highlight",
    "forest": "deep green, leaf green, moss, warm sand highlight",
    "ocean": "deep navy, teal, seafoam, clean pale highlight",
    "candy": "ink navy, rose, soft pink, bright white highlight",
    "mono": "black, graphite, silver, white",
}


def build_prompt(request: GenerateRequest) -> tuple[str, list[str]]:
    background = "transparent background" if request.transparent_background else "solid presentation background"
    prompt = (
        f"{request.description}; {ASSET_HINTS[request.asset_type]}; "
        f"{STYLE_HINTS[request.style]}; {background}; "
        f"{request.size}x{request.size}px; palette: {PALETTE_HINTS[request.palette]}; "
        "game engine friendly PNG, consistent asset pack, no watermark, no text."
    )
    constraints = [
        f"type:{request.asset_type}",
        f"style:{request.style}",
        f"size:{request.size}px",
        f"palette:{request.palette}",
        f"seed:{request.consistency_seed}",
    ]
    if request.transparent_background:
        constraints.append("transparent")
    return prompt, constraints
