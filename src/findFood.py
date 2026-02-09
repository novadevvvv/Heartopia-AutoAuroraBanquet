import cv2
import numpy as np
import pyautogui
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from .log import log
import pytesseract

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

validFoods = {
    "coffee": "Iced-Cup Coffee",
    "pancake": "Original Frosted Pancake",
    "soup": "Creamy White Radish Soup",
    "steak": "Steak w/ Mashed White Radish",
    "banquet": "Aurora Banquet"
}

def findFood(food: str | None = None) -> tuple:
    """
    OCR-detect food text on screen.
    Returns (foodKey, (x, y)) or (None, None)
    """

    if food and food not in validFoods:
        raise ValueError(f"Invalid food '{food}'")

    output_dir = Path("detectedIcons")
    output_dir.mkdir(exist_ok=True)

    screenshot = pyautogui.screenshot()
    img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Improve OCR reliability
    gray = cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY)[1]

    try:
        font = ImageFont.truetype("arial.ttf", 18)
    except:
        font = ImageFont.load_default()

    draw = ImageDraw.Draw(screenshot)

    data = pytesseract.image_to_data(
        gray,
        output_type=pytesseract.Output.DICT,
        config="--psm 6"
    )

    lines = {}
    n = len(data["text"])

    # Group words into lines
    for i in range(n):
        text = data["text"][i].strip()
        if not text:
            continue

        line_id = (data["block_num"][i], data["par_num"][i], data["line_num"][i])
        if line_id not in lines:
            lines[line_id] = []

        lines[line_id].append({
            "text": text,
            "x": data["left"][i],
            "y": data["top"][i],
            "w": data["width"][i],
            "h": data["height"][i]
        })

    best_match = (None, None)

    for foodKey, foodText in validFoods.items():
        if food and foodKey != food:
            continue

        target_words = foodText.lower().split()

        collected = []
        collected_text = []

        for line in lines.values():
            for word in line:
                collected.append(word)
                collected_text.append(word["text"].lower())

                if len(collected_text) > len(target_words):
                    collected.pop(0)
                    collected_text.pop(0)

                if collected_text == target_words:
                    xs = [w["x"] for w in collected]
                    ys = [w["y"] for w in collected]
                    ws = [w["w"] for w in collected]
                    hs = [w["h"] for w in collected]

                    x1 = min(xs)
                    y1 = min(ys)
                    x2 = max(xs[i] + ws[i] for i in range(len(ws)))
                    y2 = max(ys[i] + hs[i] for i in range(len(hs)))

                    center = (int((x1 + x2) / 2), int((y1 + y2) / 2))

                    draw.rectangle([x1, y1, x2, y2], outline="lime", width=3)
                    draw.text((x1, y1 - 20), foodKey, fill="yellow", font=font)

                    best_match = (foodKey, center)
                    screenshot.save(output_dir / "food_ocr.png")
                    return best_match

    screenshot.save(output_dir / "food_ocr.png")
    return best_match
