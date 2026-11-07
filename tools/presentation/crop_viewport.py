"""Step 1 of the slide-6 fix: crop the Isaac Sim window chrome off the two captures.

The two assets are 1024x611 window grabs of the same Isaac Sim window, so the panel
edges are fixed. Bounds were measured off the panel separators (Stage panel starts at
x=716, Content/Console at y=405, left icon rail ends at x=33, toolbar ends at y=28) and
are asserted below so a changed capture fails loudly instead of cropping silently wrong.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image

ASSETS = Path(r"C:\Users\pangw\.gemini\antigravity\scratch\csc3034-fuzzy-wildfire-sim\docs\poster\assets")
OUT = Path(r"C:\Users\pangw\.gemini\antigravity\scratch\csc3034-fuzzy-wildfire-sim\docs\presentation\assets")

BOX = (33, 28, 715, 404)  # left, top, right, bottom — viewport only

JOBS = [
    ("isaac_sim_forest_scene.png", "isaac_view_01_forest.png"),
    ("isaac_sim_drone_closeup.png", "isaac_view_02_hotspot.png"),
]


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for src_name, dst_name in JOBS:
        src = ASSETS / src_name
        im = Image.open(src).convert("RGB")
        assert im.size == (1024, 611), f"{src_name}: unexpected capture size {im.size}"

        crop = im.crop(BOX)
        arr = np.asarray(crop).astype(np.float32)
        brightness = arr.mean()

        # A viewport crop is a bright 3D scene; a mis-cropped panel is near-black.
        # Anything under 90 means the box strayed into the dark UI chrome.
        assert brightness > 90, f"{src_name}: crop looks like UI chrome (mean={brightness:.1f})"

        dst = OUT / dst_name
        crop.save(dst, optimize=True)
        kept = 100 * crop.size[0] * crop.size[1] / (im.size[0] * im.size[1])
        print(
            f"{src_name}\n"
            f"   source   {im.size[0]}x{im.size[1]}\n"
            f"   viewport x={BOX[0]}..{BOX[2]}  y={BOX[1]}..{BOX[3]}\n"
            f"   crop     {crop.size[0]}x{crop.size[1]} px  aspect {crop.size[0]/crop.size[1]:.3f}"
            f"  mean brightness {brightness:.1f}\n"
            f"   pixels kept {kept:.1f}%  -> {dst}"
        )


if __name__ == "__main__":
    main()
