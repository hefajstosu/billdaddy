import os
import warnings


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-insecure")
    if SECRET_KEY == "dev-insecure":
        warnings.warn("SECRET_KEY not set, using insecure default", stacklevel=2)
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL", "mysql+pymysql://billdaddy:billdaddy@localhost:3306/billdaddy"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "uploads")
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024
    FUZZY_THRESHOLD = int(os.getenv("FUZZY_THRESHOLD", 80))
    OCR_ENGINE = os.getenv("OCR_ENGINE", "tesseract")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
