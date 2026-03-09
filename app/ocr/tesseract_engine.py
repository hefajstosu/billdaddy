import pytesseract
from PIL import Image


def read_text(image_path):
    img = Image.open(image_path)
    return pytesseract.image_to_string(img, lang="pol")
