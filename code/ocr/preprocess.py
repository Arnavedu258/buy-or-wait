from __future__ import annotations

from pathlib import Path
import cv2
import numpy as np


class ImagePreprocessor:
    """
    OCR Image Enhancement Pipeline

    Steps
    -----
    1. Read image
    2. Convert to grayscale
    3. Remove noise
    4. Increase contrast (CLAHE)
    5. Adaptive threshold
    """

    def read(self, image_path: str | Path) -> np.ndarray:
        image = cv2.imread(str(image_path))

        if image is None:
            raise FileNotFoundError(f"Image not found: {image_path}")

        return image

    # ---------------------------------------------

    @staticmethod
    def to_grayscale(image: np.ndarray) -> np.ndarray:
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # ---------------------------------------------

    @staticmethod
    def denoise(gray: np.ndarray) -> np.ndarray:
        return cv2.fastNlMeansDenoising(gray)

    # ---------------------------------------------

    @staticmethod
    def enhance_contrast(gray: np.ndarray) -> np.ndarray:
        clahe = cv2.createCLAHE(
            clipLimit=2.0,
            tileGridSize=(8, 8),
        )

        return clahe.apply(gray)

    # ---------------------------------------------

    @staticmethod
    def threshold(gray: np.ndarray) -> np.ndarray:
        return cv2.adaptiveThreshold(
            gray,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            31,
            15,
        )

    # ---------------------------------------------

    def process(self, image_path: str | Path) -> np.ndarray:
        image = self.read(image_path)

        gray = self.to_grayscale(image)

        clean = self.denoise(gray)

        contrast = self.enhance_contrast(clean)

        binary = self.threshold(contrast)

        return binary