import cv2
import numpy as np
import pyautogui
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from ..log import log
import pytesseract
import json
from difflib import SequenceMatcher

"""
Website: https://github.com/novadevvvv
Dependencies: "log.py"
"""

# Path to Tesseract executable
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Load configuration
with open("config.json", "r") as file:
    config = json.load(file)

validFoods = config.get("foodData", {})

def findFood(food: str | None = None) -> tuple:
    """
    OCR-detect food text on screen.
    Returns (foodKey, (x, y)) or (None, None)
    """

    if food and food.lower() not in validFoods:
        raise ValueError(f"Invalid food '{food}'")

    output_dir = Path("detectedIcons")
    output_dir.mkdir(exist_ok=True)

    # Take screenshot
    screenshot = pyautogui.screenshot()
    img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

    # --- HIGH QUALITY OCR PREPROCESSING ---
    scale_factor = 2
    img = cv2.resize(img, None, fx=scale_factor, fy=scale_factor, interpolation=cv2.INTER_CUBIC)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    kernel_sharpen = np.array([[0,-1,0], [-1,5,-1], [0,-1,0]])
    gray = cv2.filter2D(gray, -1, kernel_sharpen)
    gray = cv2.GaussianBlur(gray, (3, 3), 0)
    gray = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                 cv2.THRESH_BINARY, 11, 2)
    kernel = np.ones((2, 2), np.uint8)
    gray = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, kernel)
    # --- END PREPROCESSING ---

    # Prepare for drawing
    try:
        font = ImageFont.truetype("arial.ttf", 18)
    except:
        font = ImageFont.load_default()
    draw = ImageDraw.Draw(screenshot)

    # OCR with tesseract
    data = pytesseract.image_to_data(gray, output_type=pytesseract.Output.DICT, config="--psm 6")

    # Group words into lines
    lines = {}
    n = len(data["text"])
    for i in range(n):
        text = data["text"][i].strip()
        if not text:
            continue
        line_id = (data["block_num"][i], data["par_num"][i], data["line_num"][i])
        if line_id not in lines:
            lines[line_id] = []
        lines[line_id].append({
            "text": text,
            "x": data["left"][i] // scale_factor,
            "y": data["top"][i] // scale_factor,
            "w": data["width"][i] // scale_factor,
            "h": data["height"][i] // scale_factor
        })

    best_match = (None, None)
    best_ratio = 0.0  # Track best similarity ratio

    # Search for food names
    for foodKey, foodText in validFoods.items():
        if food and foodKey != food:
            continue

        target_words = foodText.lower().split()

        for line in lines.values():
            line_words = [w["text"].lower() for w in line]
            # Slide over line to compare sequences
            for i in range(len(line_words) - len(target_words) + 1):
                window = line_words[i:i+len(target_words)]
                ratio = SequenceMatcher(None, " ".join(target_words), " ".join(window)).ratio()
                if ratio > best_ratio:
                    best_ratio = ratio
                    collected = line[i:i+len(target_words)]
                    xs = [w["x"] for w in collected]
                    ys = [w["y"] for w in collected]
                    ws = [w["w"] for w in collected]
                    hs = [w["h"] for w in collected]

                    x1 = min(xs)
                    y1 = min(ys)
                    x2 = max(xs[i] + ws[i] for i in range(len(ws)))
                    y2 = max(ys[i] + hs[i] for i in range(len(hs)))

                    center = (int((x1 + x2) / 2), int((y1 + y2) / 2))
                    best_match = (foodKey, center)

    # Draw rectangle & label for best match
    if best_match[0]:
        draw.rectangle([x1, y1, x2, y2], outline="lime", width=3)
        draw.text((x1, y1 - 20), best_match[0], fill="yellow", font=font)

    screenshot.save(output_dir / "food_ocr.png")
    return best_match
