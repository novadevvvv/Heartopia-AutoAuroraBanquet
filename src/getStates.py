import cv2
import numpy as np
import pyautogui
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from time import sleep as wait
from .log import log

settings = {
    "icons": {
        "Overheating": "overheating.png",
        "Finished": "finished.png",
        "Select Food": "selectFood.png",
        "Cooking": "cooking.png"
    },
    "paths": {
        "icons": Path("icons"),
        "output": Path("detectedIcons")
    }
}

def detectOvens():
    """
    Detects Valid Oven Symbols On Screen
    Returns Valid Ovens And Their States And Positions
    """
    output = settings["paths"]["output"]
    screenshot = pyautogui.screenshot()
    screenshot_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    cv2.imwrite(str(output / "screenshot.png"), screenshot_cv)

    try:
        font = ImageFont.truetype("arial.ttf", 20)
    except:
        font = ImageFont.load_default()

    draw = ImageDraw.Draw(screenshot)

    def nonMaxSupression(boxes, overlapThresh=0.3):
        if len(boxes) == 0:
            return []
        boxes = np.array(boxes)
        pick = []
        x1 = boxes[:,0]; y1 = boxes[:,1]; x2 = boxes[:,2]; y2 = boxes[:,3]
        area = (x2 - x1 + 1) * (y2 - y1 + 1)
        idxs = np.argsort(y2)
        while len(idxs) > 0:
            last = idxs[-1]
            pick.append(last)
            idxs = idxs[:-1]
            xx1 = np.maximum(x1[last], x1[idxs])
            yy1 = np.maximum(y1[last], y1[idxs])
            xx2 = np.minimum(x2[last], x2[idxs])
            yy2 = np.minimum(y2[last], y2[idxs])
            w_overlap = np.maximum(0, xx2 - xx1 + 1)
            h_overlap = np.maximum(0, yy2 - yy1 + 1)
            overlap = (w_overlap * h_overlap) / area[idxs]
            idxs = idxs[overlap <= overlapThresh]
        return boxes[pick].astype(int)

    # Initialize states **once**
    states = []
    global_index = 0

    for iconName, filename in settings["icons"].items():
        log(f"Verifying Icon: {iconName}")
        image_path = settings["paths"]["icons"] / filename
        log(f"Searching Path: {image_path}")
        if not image_path.exists():
            log(f"{iconName} not found at {image_path}, skipping.")
            continue

        template = cv2.imread(str(image_path), cv2.IMREAD_UNCHANGED)
        if template.shape[2] == 4:
            template_rgb = template[:, :, :3]
            mask = template[:, :, 3]
        else:
            template_rgb = template
            mask = None

        h, w = template_rgb.shape[:2]
        res = cv2.matchTemplate(screenshot_cv, template_rgb, cv2.TM_CCOEFF_NORMED, mask=mask)
        threshold = 0.8
        loc = np.where(res >= threshold)
        rects = [[pt[0], pt[1], pt[0]+w, pt[1]+h] for pt in zip(*loc[::-1])]
        filtered_rects = nonMaxSupression(rects)

        for (x1, y1, x2, y2) in filtered_rects:
            # Draw rectangle
            draw.rectangle([x1, y1, x2, y2], outline="red", width=3)
            text_position = (x1, max(y1 - 25, 0))
            draw.text(text_position, iconName, fill="yellow", font=font)

            # Cast coordinates to standard Python int
            center_x = int((x1 + x2) / 2)
            center_y = int((y1 + y2) / 2)
            coords = (center_x, center_y)


            # Append to states
            states.append([global_index, iconName, coords])
            global_index += 1

    output_path = output / "final.png"
    screenshot.save(output_path)

    return states