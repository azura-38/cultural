import os
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


class QwenEnhancer:
    """Optional Qwen prompt enhancer using DashScope OpenAI-compatible API."""

    DEFAULT_BASE_URL = "https://dashscope-intl.aliyuncs.com/compatible-mode/v1"
    DEFAULT_MODEL = "qwen-plus"

    def __init__(self) -> None:
        self.api_key = os.getenv("DASHSCOPE_API_KEY") or os.getenv("QWEN_API_KEY")
        self.base_url = os.getenv("QWEN_BASE_URL", self.DEFAULT_BASE_URL)
        self.model = os.getenv("QWEN_MODEL", self.DEFAULT_MODEL)

    @property
    def is_configured(self) -> bool:
        return bool(self.api_key)

    def enhance(self, local_result: dict[str, Any]) -> dict[str, Any]:
        if not self.is_configured:
            return {
                **local_result,
                "metadata": {
                    **local_result.get("metadata", {}),
                    "qwen_enabled": False,
                    "qwen_status": "missing_api_key",
                },
            }

        client = OpenAI(api_key=self.api_key, base_url=self.base_url)

        system_prompt = (
            "You are LIMANEX Cultural AI's senior prompt director. "
            "Improve image-generation prompts with cinematic detail, cultural respect, "
            "clear visual hierarchy, and no stereotypes. Return only the improved prompt text. "
            "Do not add explanations, markdown, quotes, or policy notes."
        )

        user_prompt = f"""
Original user idea:
{local_result['original_prompt']}

Culture:
{local_result['culture_name']}

Local cultural prompt draft:
{local_result['enhanced_prompt']}

Rewrite this as one polished professional image-generation prompt.
Keep the same culture and style direction.
Do not invent sacred/religious text.
Do not include negative prompt terms.
""".strip()

        completion = client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.7,
            max_tokens=700,
        )

        qwen_prompt = completion.choices[0].message.content.strip()

        return {
            **local_result,
            "enhanced_prompt": qwen_prompt or local_result["enhanced_prompt"],
            "local_prompt": local_result["enhanced_prompt"],
            "metadata": {
                **local_result.get("metadata", {}),
                "engine": "qwen-assisted-cultural-prompt-engine",
                "qwen_enabled": True,
                "qwen_status": "success",
                "qwen_model": self.model,
                "qwen_base_url": self.base_url,
            },
        }
