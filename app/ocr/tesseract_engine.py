import pytesseract
from PIL import Image, ImageOps


def preprocess(img):
    img = ImageOps.exif_transpose(img)
    img = img.convert("L")
    # small photos -> tesseract returns garbage
    if img.width < 1000:
        ratio = 1000 / img.width
        img = img.resize((1000, int(img.height * ratio)), Image.LANCZOS)
    img = ImageOps.autocontrast(img)
    img = img.point(lambda p: 255 if p > 150 else 0)
    return img


def read_text(image_path):
    img = preprocess(Image.open(image_path))
    return pytesseract.image_to_string(img, lang="pol", config="--psm 6")
