import sys
import os

CURRENT_DIR = os.path.dirname(__file__)
SRC_PATH = os.path.join(CURRENT_DIR, "src")
sys.path.append(SRC_PATH)

from python_ocr.models.inference import infer_page

def main():
    image_path = "/Users/dnuno/Documents/ClickNote/clicknote/python_ocr/scripts/uploaded_images_full/02_all.jpg"
    prediction = infer_page(image_path, dbg=True)

    print("Predicted Text:")
    print(prediction)

if __name__ == "__main__":
    main()