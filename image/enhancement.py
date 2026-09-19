from PIL import Image, ImageEnhance, ImageFilter
import cv2, numpy as np

def enhance(image: Image.Image, style="Premium Light") -> Image.Image:
    rgb = np.asarray(image.convert("RGB"))
    lab = cv2.cvtColor(rgb, cv2.COLOR_RGB2LAB); l, a, b = cv2.split(lab)
    l = cv2.createCLAHE(2.0, (8, 8)).apply(l)
    result = Image.fromarray(cv2.cvtColor(cv2.merge((l, a, b)), cv2.COLOR_LAB2RGB)).filter(ImageFilter.SHARPEN)
    result = ImageEnhance.Contrast(result).enhance(1.08)
    if style == "Premium Dark":
        gray = cv2.cvtColor(np.asarray(result), cv2.COLOR_RGB2GRAY)
        result = Image.fromarray(255 - cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 35, 11)).convert("RGB")
    return result
