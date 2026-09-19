import cv2
import numpy as np
from PIL import Image
from .enhancement import enhance

def prepare_crop(image, style="Premium Dark"):
    """
    Processes the raw cropped image to remove backgrounds, thicken text for projector 
    readability, and apply RGBA transparency for premium presentation templates.
    """
    # 1. Convert PIL Image to OpenCV format (NumPy array)
    open_cv_image = np.array(image)
    if len(open_cv_image.shape) == 3 and open_cv_image.shape[2] == 3:
        open_cv_image = cv2.cvtColor(open_cv_image, cv2.COLOR_RGB2BGR)
    elif len(open_cv_image.shape) == 4:
        open_cv_image = cv2.cvtColor(open_cv_image, cv2.COLOR_RGBA2BGR)

    # 2. Binarization: Strip watermarks and grey noise
    gray = cv2.cvtColor(open_cv_image, cv2.COLOR_BGR2GRAY)
    binary = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
    )

    # 3. Bold Enhancement: Morphological dilation to thicken math equations
    kernel = np.ones((2, 2), np.uint8)
    inverted = cv2.bitwise_not(binary)  # Invert to make text white (255) for dilation
    thickened = cv2.dilate(inverted, kernel, iterations=1)
    
    # 4. Transparency & Theme Mapping
    # Convert single channel back to 4-channel RGBA
    rgba = cv2.cvtColor(thickened, cv2.COLOR_GRAY2BGRA)
    
    if style == "Premium Dark":
        # Dark template: Pure white text, transparent background
        rgba[:, :, 0:3] = 255  # Set B, G, R channels to white
        rgba[:, :, 3] = thickened  # Alpha channel: Text is opaque, bg is transparent
    else:
        # Light template: Pure black text, transparent background
        rgba[:, :, 0:3] = 0    # Set B, G, R channels to black
        rgba[:, :, 3] = thickened  # Alpha channel: Text is opaque, bg is transparent
        
    # Convert the processed OpenCV array back to a PIL Image
    premium_image = Image.fromarray(rgba)
    
    # Pass the transparent, thickened image to your existing enhancement pipeline
    return enhance(premium_image, style)
