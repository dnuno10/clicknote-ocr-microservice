import sys
import os
from python_ocr.models.test_model import TestModel

CURRENT_DIR = os.path.dirname(__file__)
SRC_PATH = os.path.abspath(os.path.join(CURRENT_DIR, "..", ".."))
sys.path.append(SRC_PATH)

def main():
    labels_txt = "/Users/dnuno/Documents/ClickNote/clicknote/python_ocr/scripts/realLabels.txt"
    images_folder = "/Users/dnuno/Documents/ClickNote/clicknote/python_ocr/scripts/uploaded_images"

    test_model = TestModel(labels_txt, images_folder)

    test_model.test_predictions()

    test_model.print_summary_metrics()

    test_model.plot_metrics()

if __name__ == "__main__":
    main()