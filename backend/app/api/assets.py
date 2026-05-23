import uuid

from fastapi import APIRouter

from app.schemas.assets import GenerateRequest, GenerateResponse
from app.services.local_generator import local_generator
from app.services.prompt_builder import build_prompt

router = APIRouter()


@router.post("/generate", response_model=GenerateResponse)
def generate_assets(request: GenerateRequest) -> GenerateResponse:
    enhanced_prompt, constraints = build_prompt(request)
    assets = local_generator.generate(request, enhanced_prompt)
    return GenerateResponse(
        request_id=str(uuid.uuid4()),
        enhanced_prompt=enhanced_prompt,
        constraints=constraints,
        assets=assets,
    )
