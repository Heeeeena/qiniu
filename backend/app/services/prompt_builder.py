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

PIPELINE_HINTS = {
    "character": "export as a single sprite that can later be sliced into idle, walk, and attack frames",
    "item": "leave enough transparent padding for inventory UI, loot popups, and icon atlases",
    "tile": "keep tile edges grid-aligned and repeat-friendly for Tiled, Godot TileMap, or Unity Tile Palette",
    "background": "separate foreground readability from distant shapes for parallax layer usage",
    "ui": "use clear button states and leave center space for localization-friendly labels",
}

ENGINE_HINTS = {
    "unity": "prepare naming and sheet metadata for Unity Sprite Editor and Sprite Atlas",
    "godot": "prepare import notes for Godot Sprite2D, AtlasTexture, and TileSet workflows",
    "cocos": "prepare asset naming for Cocos Creator resources and SpriteFrame usage",
    "tiled": "prepare tile-friendly metadata for Tiled maps and external tilesets",
    "aseprite": "prepare predictable frame names for Aseprite sheet inspection and edits",
}


def build_prompt(request: GenerateRequest) -> tuple[str, list[str]]:
    background = "transparent background" if request.transparent_background else "solid presentation background"
    style_pack = f"style pack: {request.style_pack_name}; " if request.style_pack_name else ""
    naming = f"naming prefix: {request.naming_prefix}; " if request.naming_prefix else ""
    prompt = (
        f"{style_pack}{naming}{request.description}; {ASSET_HINTS[request.asset_type]}; "
        f"{STYLE_HINTS[request.style]}; {background}; "
        f"{PIPELINE_HINTS[request.asset_type]}; {ENGINE_HINTS[request.target_engine]}; "
        f"{request.size}x{request.size}px; palette: {PALETTE_HINTS[request.palette]}; "
        "game engine friendly PNG, Unity/Godot/Cocos import-ready, consistent asset pack, no watermark, no text."
    )
    constraints = [
        f"type:{request.asset_type}",
        f"style:{request.style}",
        f"size:{request.size}px",
        f"palette:{request.palette}",
        f"seed:{request.consistency_seed}",
        f"engine:{request.target_engine}",
    ]
    if request.style_pack_name:
        constraints.append(f"pack:{request.style_pack_name}")
    if request.naming_prefix:
        constraints.append(f"prefix:{request.naming_prefix}")
    if request.transparent_background:
        constraints.append("transparent")
    return prompt, constraints
