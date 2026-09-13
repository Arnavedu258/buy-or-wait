"""
OCR Package
===========

Enterprise OCR Pipeline

Flow:
    ImagePreprocessor
            ↓
      OCRExtractor
            ↓
     AmountDetector

Used for recovering missing transaction amounts from images.csv.
"""

from .preprocess import ImagePreprocessor
from .extractor import OCRExtractor, OCRResult
from .amount_detector import AmountDetector, DetectedAmount

__version__ = "1.0.0"

__all__ = [
    "ImagePreprocessor",
    "OCRExtractor",
    "OCRResult",
    "AmountDetector",
    "DetectedAmount",
]