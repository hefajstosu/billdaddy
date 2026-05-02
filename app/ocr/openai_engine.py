import base64
import json
import mimetypes
import re
from datetime import date
from decimal import Decimal

from flask import current_app
from openai import OpenAI

PROMPT = """Read this Polish shop receipt. Return JSON only:
{"shop": str|null, "date": "YYYY-MM-DD"|null, "total": number|null,
 "items": [{"raw_name": str, "quantity": number, "price": number, "category": str}]}
raw_name exactly as printed, price = price per unit.
category must be one of: %s"""


def load_json(text):
    # model likes to wrap it in ```json ... ``` even when asked not to
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text.strip())
    return json.loads(text)


def extract(image_path, categories):
    client = OpenAI(api_key=current_app.config["OPENAI_API_KEY"], timeout=30)

    mime = mimetypes.guess_type(image_path)[0] or "image/jpeg"
    with open(image_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()

    resp = client.chat.completions.create(
        model=current_app.config["OPENAI_MODEL"],
        messages=[{
            "role": "user",
            "content": [
                {"type": "text", "text": PROMPT % ", ".join(categories)},
                {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{b64}"}},
            ],
        }],
        temperature=0,
        response_format={"type": "json_object"},
    )
    data = load_json(resp.choices[0].message.content)

    result = {
        "shop": data.get("shop"),
        "date": None,
        "total": Decimal(str(data["total"])) if data.get("total") is not None else None,
        "items": [],
    }
    if data.get("date"):
        try:
            result["date"] = date.fromisoformat(data["date"])
        except ValueError:
            pass
    for it in data.get("items", []):
        result["items"].append({
            "raw_name": it["raw_name"],
            "quantity": Decimal(str(it.get("quantity") or 1)),
            "price": Decimal(str(it["price"])),
            "category": it.get("category"),
        })
    return result
