from flask import current_app

from ..models import Category
from . import openai_engine
from .parser import parse
from .tesseract_engine import read_text


class OcrError(Exception):
    """OCR failed in a way the user can do something about (bad photo, bad key)."""


def extract(image_path):
    try:
        if current_app.config["OCR_ENGINE"] == "openai":
            names = [c.name for c in Category.query.all()]
            return openai_engine.extract(image_path, names)
        return parse(read_text(image_path))
    except OcrError:
        raise
    except Exception as e:
        raise OcrError(f"could not read receipt: {e}") from e
