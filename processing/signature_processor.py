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
    def auto_crop_signature(gray_image):
        """
        Detect signature bounds and return a tightly cropped image.
        Returns None if the canvas is completely blank.
        """
        # Find bounding box, ignoring near-white pixels
        bbox = gray_image.point(lambda p: 255 if p < 250 else 0).getbbox()

        if not bbox:
            return None

        left, top, right, bottom = bbox

        # Apply configurable crop margin with boundary checks
        left = max(0, left - CROP_MARGIN)
        top = max(0, top - CROP_MARGIN)
        right = min(gray_image.width, right + CROP_MARGIN)
        bottom = min(gray_image.height, bottom + CROP_MARGIN)

        return gray_image.crop((left, top, right, bottom))

    @staticmethod
    def process(image, transparent=False):
        # 1. Grayscale Conversion
        gray = image.convert("L")

        # 2. Auto Crop Signature
        cropped = SignatureProcessor.auto_crop_signature(gray)

        # Handle empty canvas scenario
        if not cropped:
            if transparent:
                return Image.new("RGBA", (EXPORT_WIDTH, EXPORT_HEIGHT), (0, 0, 0, 0))
            return Image.new("L", (EXPORT_WIDTH, EXPORT_HEIGHT), 255)

        # 3. Convert to numpy array for fast manipulation
        arr = np.asarray(cropped, dtype=np.float32)

        # 4. Curve Enhancement (Gamma Correction)
        arr = 255 * (arr / 255) ** CURVE_GAMMA
        arr = np.clip(arr, 0, 255)

        # 5. Threshold Cleanup
        arr = np.where(arr > WHITE_THRESHOLD, 255, 0)
        processed = Image.fromarray(arr.astype(np.uint8))

        # 6. Stroke Thickening
        inverted = ImageOps.invert(processed)
        inverted = inverted.filter(ImageFilter.MaxFilter(STROKE_THICKEN_KERNEL))
        processed = ImageOps.invert(inverted)

        # 7. Fit and Center
        available_width = EXPORT_WIDTH - (PADDING * 2)
        available_height = EXPORT_HEIGHT - (PADDING * 2)

        ratio = min(
            available_width / processed.width,
            available_height / processed.height,
        )

        new_width = int(processed.width * ratio)
        new_height = int(processed.height * ratio)

        resized = processed.resize((new_width, new_height), Image.Resampling.LANCZOS)

        x = (EXPORT_WIDTH - new_width) // 2
        y = (EXPORT_HEIGHT - new_height) // 2

        # 8. Export Formatting
        if transparent:
            canvas = Image.new("RGBA", (EXPORT_WIDTH, EXPORT_HEIGHT), (0, 0, 0, 0))
            alpha_mask = ImageOps.invert(resized)
            transparent_sig = Image.new("RGBA", resized.size, (0, 0, 0, 255))
            transparent_sig.putalpha(alpha_mask)
            canvas.paste(transparent_sig, (x, y), transparent_sig)
        else:
            canvas = Image.new("L", (EXPORT_WIDTH, EXPORT_HEIGHT), 255)
            canvas.paste(resized, (x, y))

        return canvas