from __future__ import annotations

import numpy as np
from PIL import Image


class Transformations:
    # Default severity used for the three anomalous-trichromacy (partial) types.
    # 0.0 = unaffected (identity), 1.0 = full dichromacy.
    ANOMALOUS_SEVERITY = 0.6

    # Blend factor for achromatomaly (partial): 0.0 = original color,
    # 1.0 = full achromatopsia grayscale.
    ACHROMATOMALY_BLEND = 0.5

    IDENTITY = np.eye(3)

    # Source: Machado, G. M., Oliveira, M. M., & Fernandes, L. A. F. (2009).
    # "A Physiologically-based Model for Simulation of Color Vision Deficiency."
    # IEEE Transactions on Visualization and Computer Graphics, 15(6), 1291-1298.
    # doi:10.1109/TVCG.2009.113 -- severity = 1.0 (full dichromacy) matrices.
    PROTANOPIA = np.array(
        [
            [0.152286, 1.052583, -0.204868],
            [0.114503, 0.786281, 0.099216],
            [-0.003882, -0.048116, 1.051998],
        ]
    )

    # Source: Machado, Oliveira & Fernandes (2009), doi:10.1109/TVCG.2009.113 --
    # severity = 1.0 (full dichromacy) matrices.
    DEUTERANOPIA = np.array(
        [
            [0.367322, 0.860646, -0.227968],
            [0.280085, 0.672501, 0.047413],
            [-0.011820, 0.042940, 0.968881],
        ]
    )

    # Source: Machado, Oliveira & Fernandes (2009), doi:10.1109/TVCG.2009.113 --
    # severity = 1.0 (full dichromacy) matrices.
    TRITANOPIA = np.array(
        [
            [1.255528, -0.076749, -0.178779],
            [-0.078411, 0.930809, 0.147602],
            [0.004733, 0.691367, 0.303900],
        ]
    )

    # Luma coefficients per ITU-R Recommendation BT.709-6 (06/2015), used for the
    # achromatopsia (total color blindness) grayscale conversion.
    # https://www.itu.int/rec/R-REC-BT.709
    LUMA_WEIGHTS = np.array([0.2126, 0.7152, 0.0722])

    @staticmethod
    def anomalous_matrix(dichromat_matrix: np.ndarray, severity: float) -> np.ndarray:
        """Approximate an anomalous-trichromacy matrix as a linear interpolation
        between identity (severity=0) and the full dichromat matrix (severity=1).

        This is a simplification of Machado, Oliveira & Fernandes (2009)
        (doi:10.1109/TVCG.2009.113), which instead tabulates matrices at
        discrete intermediate severities. Interpolating linearly is a
        reasonable approximation.
        """
        return (1 - severity) * Transformations.IDENTITY + severity * dichromat_matrix

    @staticmethod
    def apply_matrix(image: Image.Image, matrix: np.ndarray) -> Image.Image:
        rgb = image.convert("RGB")
        pixels = np.asarray(rgb, dtype=np.float64).reshape(-1, 3)
        transformed = pixels @ matrix.T
        transformed = np.clip(transformed, 0, 255).astype(np.uint8)
        return Image.fromarray(transformed.reshape(*rgb.size[::-1], 3), mode="RGB")

    @staticmethod
    def identity(image: Image.Image) -> Image.Image:
        return image.convert("RGB")

    @staticmethod
    def protanopia(image: Image.Image) -> Image.Image:
        return Transformations.apply_matrix(image, Transformations.PROTANOPIA)

    @staticmethod
    def deuteranopia(image: Image.Image) -> Image.Image:
        return Transformations.apply_matrix(image, Transformations.DEUTERANOPIA)

    @staticmethod
    def tritanopia(image: Image.Image) -> Image.Image:
        return Transformations.apply_matrix(image, Transformations.TRITANOPIA)

    @staticmethod
    def protanomaly(image: Image.Image) -> Image.Image:
        matrix = Transformations.anomalous_matrix(Transformations.PROTANOPIA, Transformations.ANOMALOUS_SEVERITY)
        return Transformations.apply_matrix(image, matrix)

    @staticmethod
    def deuteranomaly(image: Image.Image) -> Image.Image:
        matrix = Transformations.anomalous_matrix(Transformations.DEUTERANOPIA, Transformations.ANOMALOUS_SEVERITY)
        return Transformations.apply_matrix(image, matrix)

    @staticmethod
    def tritanomaly(image: Image.Image) -> Image.Image:
        matrix = Transformations.anomalous_matrix(Transformations.TRITANOPIA, Transformations.ANOMALOUS_SEVERITY)
        return Transformations.apply_matrix(image, matrix)

    @staticmethod
    def achromatopsia(image: Image.Image) -> Image.Image:
        rgb = image.convert("RGB")
        pixels = np.asarray(rgb, dtype=np.float64).reshape(-1, 3)
        luma = pixels @ Transformations.LUMA_WEIGHTS
        gray = np.clip(luma, 0, 255).astype(np.uint8)
        gray_rgb = np.repeat(gray[:, np.newaxis], 3, axis=1)
        return Image.fromarray(gray_rgb.reshape(*rgb.size[::-1], 3), mode="RGB")

    @staticmethod
    def achromatomaly(image: Image.Image) -> Image.Image:
        rgb = image.convert("RGB")
        original = np.asarray(rgb, dtype=np.float64)
        gray = np.asarray(Transformations.achromatopsia(rgb), dtype=np.float64)
        blended = (1 - Transformations.ACHROMATOMALY_BLEND) * original + Transformations.ACHROMATOMALY_BLEND * gray
        return Image.fromarray(np.clip(blended, 0, 255).astype(np.uint8), mode="RGB")
