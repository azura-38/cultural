from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from prompt_engine import CultureNotFoundError, CulturalPromptEngine
from qwen_client import QwenEnhancer

app = FastAPI(
    title="LIMANEX Cultural AI",
    description="A Qwen-assisted cultural image prompt generation API.",
    version="1.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

engine = CulturalPromptEngine()
qwen = QwenEnhancer()


class GenerateRequest(BaseModel):
    prompt: str = Field(..., min_length=3, description="The user's base image idea.")
    culture: str = Field(..., min_length=2, description="Culture key such as turkish.")
    style: str = Field("cinematic", description="Visual style preset.")
    quality: str = Field("high", description="Quality preset.")
    use_qwen: bool = Field(True, description="Use Qwen API if the API key is configured.")


@app.get("/")
def root():
    return {
        "message": "LIMANEX Cultural AI API is running",
        "version": "1.1.0",
        "qwen_configured": qwen.is_configured,
        "qwen_model": qwen.model,
    }


@app.get("/cultures")
def get_cultures():
    return {
        "cultures": engine.list_cultures(),
        "styles": engine.supported_styles,
        "qualities": engine.supported_qualities,
        "qwen_configured": qwen.is_configured,
    }


@app.post("/generate")
def generate(data: GenerateRequest):
    try:
        result = engine.generate(
            prompt=data.prompt,
            culture_id=data.culture,
            style=data.style,
            quality=data.quality,
        )

        if data.use_qwen:
            try:
                return qwen.enhance(result)
            except Exception as exc:
                return {
                    **result,
                    "metadata": {
                        **result.get("metadata", {}),
                        "qwen_enabled": True,
                        "qwen_status": "error",
                        "qwen_error": str(exc),
                    },
                }

        return {
            **result,
            "metadata": {
                **result.get("metadata", {}),
                "qwen_enabled": False,
                "qwen_status": "disabled_by_request",
            },
        }
    except CultureNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
