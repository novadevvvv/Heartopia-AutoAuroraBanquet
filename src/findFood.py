import cv2
import numpy as np
import pyautogui
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from .log import log

assetPath = Path("icons/food")
validFoods = ["coffee", "pancake", "soup", "steak"]

def findFood(food: str | None = None) -> tuple:
    """
    Detect food icon(s) on screen.
    If `food` is provided, only searches for that food.
    Returns (foodName, (x, y)) or (None, None)
    Also saves annotated image to detectedIcons/food.png
    """

    if food and food not in validFoods:
        raise ValueError(f"Invalid food '{food}'. Valid options: {validFoods}")

    output_dir = Path("detectedIcons")
    output_dir.mkdir(exist_ok=True)

    screenshot = pyautogui.screenshot()
    screenshot_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

    try:
        font = ImageFont.truetype("arial.ttf", 20)
    except:
        font = ImageFont.load_default()

    draw = ImageDraw.Draw(screenshot)

    foods_to_check = [food] if food else validFoods

    best_match = (None, None)
    best_score = 0.0

    for foodName in foods_to_check:
        icon_path = assetPath / f"{foodName}.png"
        log(f"Searching food icon: {icon_path}")

        if not icon_path.exists():
            log(f"Food icon not found: {icon_path}")
            continue

        template = cv2.imread(str(icon_path), cv2.IMREAD_UNCHANGED)

        if template.shape[2] == 4:
            template_rgb = template[:, :, :3]
            mask = template[:, :, 3]
        else:
            template_rgb = template
            mask = None

        h, w = template_rgb.shape[:2]

        res = cv2.matchTemplate(
            screenshot_cv,
            template_rgb,
            cv2.TM_CCOEFF_NORMED,
            mask=mask
        )

        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

        if max_val < 0.75:
            continue

        if max_val > best_score:
            x1, y1 = max_loc
            x2, y2 = x1 + w, y1 + h

            center_x = int((x1 + x2) / 2)
            center_y = int((y1 + y2) / 2)

            best_match = (foodName, (center_x, center_y))
            best_score = max_val

            # draw
            draw.rectangle([x1, y1, x2, y2], outline="lime", width=3)
            draw.text((x1, max(0, y1 - 25)), foodName, fill="yellow", font=font)

    screenshot.save(output_dir / "food.png")

    return best_match
