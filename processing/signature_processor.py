from PIL import (
    Image,
    ImageFilter,
    ImageOps,
)

import numpy as np

from config import (
    EXPORT_WIDTH,
    EXPORT_HEIGHT,
    PADDING,
    CROP_MARGIN,
    CURVE_GAMMA,
    WHITE_THRESHOLD,
    STROKE_THICKEN_KERNEL,
)


class SignatureProcessor:

    @staticmethod
    def process(image):

        gray = image.convert("L")

        bbox = gray.point(
            lambda p:
            255 if p < 250 else 0
        ).getbbox()

        if not bbox:

            return Image.new(
                "L",
                (
                    EXPORT_WIDTH,
                    EXPORT_HEIGHT,
                ),
                255,
            )

        left, top, right, bottom = bbox

        left = max(
            0,
            left - CROP_MARGIN
        )

        top = max(
            0,
            top - CROP_MARGIN
        )

        right = min(
            gray.width,
            right + CROP_MARGIN
        )

        bottom = min(
            gray.height,
            bottom + CROP_MARGIN
        )

        cropped = gray.crop(
            (
                left,
                top,
                right,
                bottom,
            )
        )

        arr = np.asarray(
            cropped,
            dtype=np.float32
        )

        arr = 255 * (
            arr / 255
        ) ** CURVE_GAMMA

        arr = np.clip(
            arr,
            0,
            255
        )

        arr = np.where(
            arr > WHITE_THRESHOLD,
            255,
            0
        )

        processed = Image.fromarray(
            arr.astype(np.uint8)
        )

        inverted = ImageOps.invert(
            processed
        )

        inverted = inverted.filter(
            ImageFilter.MaxFilter(
                STROKE_THICKEN_KERNEL
            )
        )

        processed = ImageOps.invert(
            inverted
        )

        available_width = (
            EXPORT_WIDTH
            - PADDING * 2
        )

        available_height = (
            EXPORT_HEIGHT
            - PADDING * 2
        )

        ratio = min(
            available_width
            / processed.width,
            available_height
            / processed.height,
        )

        new_width = int(
            processed.width
            * ratio
        )

        new_height = int(
            processed.height
            * ratio
        )

        resized = processed.resize(
            (
                new_width,
                new_height,
            ),
            Image.Resampling.LANCZOS,
        )

        canvas = Image.new(
            "L",
            (
                EXPORT_WIDTH,
                EXPORT_HEIGHT,
            ),
            255,
        )

        x = (
            EXPORT_WIDTH
            - new_width
        ) // 2

        y = (
            EXPORT_HEIGHT
            - new_height
        ) // 2

        canvas.paste(
            resized,
            (
                x,
                y,
            )
        )

        return canvas