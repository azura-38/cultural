from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from prompt_engine import CultureNotFoundError, CulturalPromptEngine

app = FastAPI(
    title="LIMANEX Cultural AI",
    description="A zero-budget cultural image prompt generation API.",
    version="1.0.0",
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


class GenerateRequest(BaseModel):
    prompt: str = Field(..., min_length=3, description="The user's base image idea.")
    culture: str = Field(..., min_length=2, description="Culture key such as turkish.")
    style: str = Field("cinematic", description="Visual style preset.")
    quality: str = Field("high", description="Quality preset.")


@app.get("/")
def root():
    return {
        "message": "LIMANEX Cultural AI API is running",
        "version": "1.0.0",
    }


@app.get("/cultures")
def get_cultures():
    return {
        "cultures": engine.list_cultures(),
        "styles": engine.supported_styles,
        "qualities": engine.supported_qualities,
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
        return result
    except CultureNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
