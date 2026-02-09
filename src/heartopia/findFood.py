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

def findFood(food: str, index: int = 0) -> tuple:
    """
    OCR-detect food text on screen.
    index = 0 -> best match
    index = 1 -> second-best match
    Returns (foodKey, (x, y)) or (None, None)
    """

    if food and food.lower() not in validFoods:
        raise ValueError(f"Invalid food '{food}'")

    output_dir = Path("detectedIcons")
    output_dir.mkdir(exist_ok=True)

    screenshot = pyautogui.screenshot()
    img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

    # --- OCR PREPROCESSING ---
    scale_factor = 2
    img = cv2.resize(img, None, fx=scale_factor, fy=scale_factor, interpolation=cv2.INTER_CUBIC)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.filter2D(gray, -1, np.array([[0,-1,0], [-1,5,-1], [0,-1,0]]))
    gray = cv2.GaussianBlur(gray, (3, 3), 0)
    gray = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY, 11, 2
    )
    gray = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, np.ones((2, 2), np.uint8))
    # --- END PREPROCESSING ---

    draw = ImageDraw.Draw(screenshot)
    try:
        font = ImageFont.truetype("arial.ttf", 18)
    except:
        font = ImageFont.load_default()

    data = pytesseract.image_to_data(
        gray,
        output_type=pytesseract.Output.DICT,
        config="--psm 6"
    )

    # Group OCR words into lines
    lines = {}
    for i, text in enumerate(data["text"]):
        text = text.strip()
        if not text:
            continue

        line_id = (data["block_num"][i], data["par_num"][i], data["line_num"][i])
        lines.setdefault(line_id, []).append({
            "text": text,
            "x": data["left"][i] // scale_factor,
            "y": data["top"][i] // scale_factor,
            "w": data["width"][i] // scale_factor,
            "h": data["height"][i] // scale_factor
        })

    matches = []  # (ratio, foodKey, center, bbox)

    for foodKey, foodText in validFoods.items():
        if food and foodKey != food:
            continue

        target_words = foodText.lower().split()

        for line in lines.values():
            words = [w["text"].lower() for w in line]

            for i in range(len(words) - len(target_words) + 1):
                window = words[i:i + len(target_words)]
                ratio = SequenceMatcher(
                    None,
                    " ".join(target_words),
                    " ".join(window)
                ).ratio()

                if ratio < 0.6:
                    continue

                collected = line[i:i + len(target_words)]
                xs = [w["x"] for w in collected]
                ys = [w["y"] for w in collected]
                ws = [w["w"] for w in collected]
                hs = [w["h"] for w in collected]

                x1 = min(xs)
                y1 = min(ys)
                x2 = max(xs[j] + ws[j] for j in range(len(ws)))
                y2 = max(ys[j] + hs[j] for j in range(len(hs)))

                center = (int((x1 + x2) / 2), int((y1 + y2) / 2))

                matches.append((ratio, foodKey, center, (x1, y1, x2, y2)))

    if not matches:
        return (None, None)

    # Sort best → worst
    matches.sort(key=lambda m: m[0], reverse=True)

    # Draw bounding box for BEST match only
    _, best_key, _, (x1, y1, x2, y2) = matches[0]
    draw.rectangle([x1, y1, x2, y2], outline="lime", width=3)
    draw.text((x1, y1 - 20), best_key, fill="yellow", font=font)

    screenshot.save(output_dir / "food_ocr.png")

    if index is None or index >= len(matches):
        return (None, None)

    _, foodKey, center, _ = matches[index]
    return (foodKey, center)
