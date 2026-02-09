import cv2
import numpy as np
import pyautogui
from pathlib import Path
from time import time
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
    },
    "scale_factor": 0.5,   # downscale for speed
    "threshold": 0.8       # template match threshold
}

# Preload templates once
templates = {}
for iconName, filename in settings["icons"].items():
    path = settings["paths"]["icons"] / filename
    if path.exists():
        tmpl = cv2.imread(str(path), cv2.IMREAD_UNCHANGED)
        if tmpl.shape[2] == 4:
            templates[iconName] = (cv2.cvtColor(tmpl[:, :, :3], cv2.COLOR_BGR2GRAY), tmpl[:, :, 3])
        else:
            templates[iconName] = (cv2.cvtColor(tmpl, cv2.COLOR_BGR2GRAY), None)
    else:
        log(f"Template not found: {path}")

def nonMaxSuppression(boxes, overlapThresh=0.3):
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
        w = np.maximum(0, xx2 - xx1 + 1)
        h = np.maximum(0, yy2 - yy1 + 1)
        overlap = (w * h) / area[idxs]
        idxs = idxs[overlap <= overlapThresh]
    return boxes[pick].astype(int)

def detectOvens():
    """
    Detects valid oven icons on screen and returns their states and positions.
    Optimized for speed (~0.25s per frame)
    """
    start_time = time()
    output_path = settings["paths"]["output"]
    output_path.mkdir(exist_ok=True, parents=True)

    # Full screenshot, then resize for speed
    screenshot = pyautogui.screenshot()
    screenshot_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    scale = settings["scale_factor"]
    screenshot_small = cv2.resize(screenshot_cv, (0,0), fx=scale, fy=scale)
    screenshot_gray = cv2.cvtColor(screenshot_small, cv2.COLOR_BGR2GRAY)

    states = []
    idx = 0

    for iconName, (template_gray, mask) in templates.items():
        log(f"Detecting: {iconName}")
        if template_gray is None:
            continue

        h, w = template_gray.shape[:2]

        # Resize template to match screenshot scale
        if scale != 1.0:
            template_small = cv2.resize(template_gray, (int(w*scale), int(h*scale)), interpolation=cv2.INTER_AREA)
            if mask is not None:
                mask_small = cv2.resize(mask, (int(w*scale), int(h*scale)), interpolation=cv2.INTER_AREA)
            else:
                mask_small = None
        else:
            template_small = template_gray
            mask_small = mask

        res = cv2.matchTemplate(screenshot_gray, template_small, cv2.TM_CCOEFF_NORMED, mask=mask_small)
        loc = np.where(res >= settings["threshold"])
        rects = [[int(pt[0]), int(pt[1]), int(pt[0]+template_small.shape[1]), int(pt[1]+template_small.shape[0])] for pt in zip(*loc[::-1])]
        rects = nonMaxSuppression(rects)

        for (x1, y1, x2, y2) in rects:
            # Scale coordinates back to full resolution
            center_x = int((x1 + x2) / (2*scale))
            center_y = int((y1 + y2) / (2*scale))
            states.append([idx, iconName, (center_x, center_y)])
            idx += 1

    elapsed = time() - start_time
    log(f"Oven detection done in {elapsed:.3f}s. Found {len(states)} icons.")
    return states
