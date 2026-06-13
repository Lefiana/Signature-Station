import os
from pathlib import Path

CANVAS_WIDTH = 900
CANVAS_HEIGHT = 300

EXPORT_WIDTH = 200
EXPORT_HEIGHT = 89

EXPORT_DPI = 150

PEN_WIDTH = 4

PADDING = 8

CROP_MARGIN = 5

CURVE_GAMMA = 1.8

WHITE_THRESHOLD = 200

STROKE_THICKEN_KERNEL = 3

# ---------------------------------------------------------
# NETWORK SAVE SETUP
# ---------------------------------------------------------
# Replace "ID-MAKER-PC" with the actual computer name of the ID PC
# Replace "SignaturesShare" with the name of the shared folder
NETWORK_PATH = Path(r"\\ID-MAKER-PC\SignaturesShare")

# Check if the network path is reachable and writable
if NETWORK_PATH.exists() and os.access(NETWORK_PATH, os.W_OK):
    OUTPUT_FOLDER = NETWORK_PATH
    print(f"Connected to network folder: {OUTPUT_FOLDER}")
else:
    # Fallback to local storage if the network is down
    OUTPUT_FOLDER = Path("output/signatures")
    OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)
    print(f"Network unreachable. Falling back to local: {OUTPUT_FOLDER}")