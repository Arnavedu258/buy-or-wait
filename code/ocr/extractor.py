from __future__ import annotations

from dataclasses import dataclass
from typing import List

import easyocr
import numpy as np


# ==========================================================
# OCR Result Model
# ==========================================================

@dataclass(slots=True)
class OCRResult:
    text: str
    confidence: float
    bbox: list


# ==========================================================
# EasyOCR Engine
# ==========================================================

class OCRExtractor:
    """
    Enterprise OCR Engine

    Features
    --------
    • Singleton EasyOCR model
    • Confidence filtering
    • Structured output
    """

    _reader = None

    def __init__(self, languages: list[str] | None = None):
        if languages is None:
            languages = ["en"]

        if OCRExtractor._reader is None:
            OCRExtractor._reader = easyocr.Reader(
                languages,
                gpu=False
            )

        self.reader = OCRExtractor._reader

    # ------------------------------------------------------

    def extract(
        self,
        image: np.ndarray,
        min_confidence: float = 0.45,
    ) -> List[OCRResult]:

        raw = self.reader.readtext(image)

        results: List[OCRResult] = []

        for bbox, text, score in raw:

            if score < min_confidence:
                continue

            results.append(
                OCRResult(
                    text=text.strip(),
                    confidence=round(float(score), 3),
                    bbox=bbox,
                )
            )

        return results

    # ------------------------------------------------------

    @staticmethod
    def as_text(results: List[OCRResult]) -> str:
        return " ".join(r.text for r in results)