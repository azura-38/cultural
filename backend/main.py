from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import replicate
import os
from dotenv import load_dotenv

# 🔥 ENV LOAD
load_dotenv()

token = os.getenv("REPLICATE_API_TOKEN")

if not token:
    raise ValueError("❌ REPLICATE_API_TOKEN bulunamadı (.env kontrol et)")

os.environ["REPLICATE_API_TOKEN"] = token

# 🔥 APP
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PromptRequest(BaseModel):
    prompt: str
    culture: str

@app.get("/")
def root():
    return {"message": "API çalışıyor 🚀"}

# 🔥 TEK generate endpoint
@app.post("/generate")
def generate(data: PromptRequest):
    try:
        final_prompt = f"""
        {data.prompt} in {data.culture} culture,
        traditional clothing, cultural symbols,
        ultra realistic, cinematic lighting, highly detailed
        """

        output = replicate.run(
            "stability-ai/sdxl-turbo:da77bc59ee60423279fd632efb4795ab731d9e3ca9705ef3341091fb989b7eaf",
            input={
                "prompt": final_prompt
            }
        )

        return {
            "prompt": final_prompt,
            "image": output[0]
        }

    except Exception as e:
        return {"error": str(e)}