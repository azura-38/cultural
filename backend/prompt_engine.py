import json
from pathlib import Path
from typing import Any


class CultureNotFoundError(Exception):
    """Raised when a selected culture does not exist in the local dataset."""


class CulturalPromptEngine:
    """Local prompt engine for LIMANEX Cultural AI.

    This engine does not call any paid or external AI service. It transforms a
    user's simple image idea into a culturally rich image-generation prompt by
    combining local JSON culture data with style and quality presets.
    """

    STYLE_PRESETS: dict[str, str] = {
        "cinematic": (
            "cinematic composition, dramatic but natural lighting, depth of field, "
            "wide establishing atmosphere, emotionally grounded storytelling"
        ),
        "portrait": (
            "centered portrait composition, expressive face, detailed costume design, "
            "soft background separation, refined character-focused framing"
        ),
        "fantasy": (
            "mythic fantasy atmosphere, symbolic visual language, subtle supernatural "
            "energy, grand scale, painterly imagination"
        ),
        "historical": (
            "historically inspired composition, grounded materials, museum-quality "
            "detail, respectful period atmosphere, documentary realism"
        ),
        "game_art": (
            "stylized premium game art, readable silhouette, polished shapes, clear "
            "material separation, mobile-game friendly visual hierarchy"
        ),
        "anime": (
            "high-end anime key visual, elegant linework, expressive staging, luminous "
            "background detail, dynamic but clean composition"
        ),
        "realistic": (
            "realistic photography-inspired rendering, natural proportions, believable "
            "materials, authentic lighting, grounded environment design"
        ),
    }

    QUALITY_PRESETS: dict[str, str] = {
        "draft": "clean concept art, readable composition, balanced details",
        "high": "high detail, sharp focus, balanced contrast, polished professional image prompt",
        "ultra": "ultra-detailed, premium production design, intricate texture work, cinematic realism",
    }

    BASE_NEGATIVE_PROMPT = (
        "low quality, blurry, pixelated, distorted anatomy, extra fingers, broken hands, "
        "bad proportions, duplicate face, text artifacts, watermark, logo, oversaturated, "
        "flat lighting, messy composition, disrespectful caricature, cultural stereotype"
    )

    def __init__(self, data_dir: Path | None = None) -> None:
        self.data_dir = data_dir or Path(__file__).parent / "data" / "cultures"
        self._cultures = self._load_cultures()

    @property
    def supported_styles(self) -> list[str]:
        return list(self.STYLE_PRESETS.keys())

    @property
    def supported_qualities(self) -> list[str]:
        return list(self.QUALITY_PRESETS.keys())

    def _load_cultures(self) -> dict[str, dict[str, Any]]:
        cultures: dict[str, dict[str, Any]] = {}

        if not self.data_dir.exists():
            raise FileNotFoundError(f"Culture data directory not found: {self.data_dir}")

        for file_path in sorted(self.data_dir.glob("*.json")):
            with file_path.open("r", encoding="utf-8") as file:
                culture = json.load(file)

            culture_id = culture.get("id") or file_path.stem
            culture["id"] = culture_id
            cultures[culture_id] = culture

        return cultures

    def list_cultures(self) -> list[dict[str, str]]:
        return [
            {
                "id": culture["id"],
                "name": culture.get("name", culture["id"].title()),
                "description": culture.get("description", ""),
            }
            for culture in self._cultures.values()
        ]

    def _get_culture(self, culture_id: str) -> dict[str, Any]:
        normalized_id = culture_id.strip().lower()

        if normalized_id not in self._cultures:
            available = ", ".join(sorted(self._cultures.keys()))
            raise CultureNotFoundError(
                f"Culture '{culture_id}' was not found. Available cultures: {available}"
            )

        return self._cultures[normalized_id]

    @staticmethod
    def _join_terms(culture: dict[str, Any], key: str, limit: int = 5) -> str:
        values = culture.get(key, [])
        if not values:
            return "subtle culturally relevant details"
        return ", ".join(values[:limit])

    def _build_negative_prompt(self, culture: dict[str, Any]) -> str:
        avoid_terms = culture.get("avoid", [])
        if not avoid_terms:
            return self.BASE_NEGATIVE_PROMPT

        return f"{self.BASE_NEGATIVE_PROMPT}, {', '.join(avoid_terms)}"

    def generate(
        self,
        prompt: str,
        culture_id: str,
        style: str = "cinematic",
        quality: str = "high",
    ) -> dict[str, Any]:
        clean_prompt = " ".join(prompt.strip().split())

        if not clean_prompt:
            raise ValueError("Prompt cannot be empty.")

        normalized_style = style.strip().lower()
        normalized_quality = quality.strip().lower()

        if normalized_style not in self.STYLE_PRESETS:
            available = ", ".join(self.supported_styles)
            raise ValueError(f"Unsupported style '{style}'. Available styles: {available}")

        if normalized_quality not in self.QUALITY_PRESETS:
            available = ", ".join(self.supported_qualities)
            raise ValueError(
                f"Unsupported quality '{quality}'. Available qualities: {available}"
            )

        culture = self._get_culture(culture_id)
        culture_name = culture.get("name", culture["id"].title())

        enhanced_prompt_parts = [
            clean_prompt,
            f"reimagined through {culture_name} visual identity",
            culture.get("description", "respectful cultural visual language"),
            f"clothing and character details: {self._join_terms(culture, 'clothing')}",
            f"symbols and ornamental language: {self._join_terms(culture, 'symbols')}",
            f"architecture and setting: {self._join_terms(culture, 'architecture')}",
            f"materials and surfaces: {self._join_terms(culture, 'materials')}",
            f"color palette: {self._join_terms(culture, 'colors')}",
            f"environmental cues: {self._join_terms(culture, 'environment')}",
            f"mythological or poetic accents: {self._join_terms(culture, 'mythology')}",
            f"art direction references: {self._join_terms(culture, 'art_style')}",
            self.STYLE_PRESETS[normalized_style],
            self.QUALITY_PRESETS[normalized_quality],
            (
                "respectful cultural fusion, no caricature, no costume-party look, "
                "cohesive worldbuilding, strong silhouette, professional image-generation prompt"
            ),
        ]

        enhanced_prompt = ", ".join(part for part in enhanced_prompt_parts if part)

        return {
            "original_prompt": clean_prompt,
            "culture": culture["id"],
            "culture_name": culture_name,
            "enhanced_prompt": enhanced_prompt,
            "negative_prompt": self._build_negative_prompt(culture),
            "metadata": {
                "style": normalized_style,
                "quality": normalized_quality,
                "engine": "local-cultural-prompt-engine",
            },
        }
