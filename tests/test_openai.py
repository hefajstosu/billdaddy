from datetime import date
from decimal import Decimal
from types import SimpleNamespace

from app.ocr import openai_engine

ANSWER = """```json
{"shop": "Lidl", "date": "2026-11-16", "total": 11.28,
 "items": [{"raw_name": "MLEKO LACIATE 3.2%", "quantity": 1, "price": 3.79, "category": "Nabiał"},
           {"raw_name": "COCA COLA 1,5L", "quantity": 1, "price": 7.49, "category": "Napoje"}]}
```"""


class FakeClient:
    def __init__(self, **kw):
        self.chat = SimpleNamespace(completions=SimpleNamespace(create=self.create))

    def create(self, **kw):
        msg = SimpleNamespace(content=ANSWER)
        return SimpleNamespace(choices=[SimpleNamespace(message=msg)])


def test_openai_engine(app, monkeypatch, tmp_path):
    img = tmp_path / "p.jpg"
    img.write_bytes(b"x")
    monkeypatch.setattr(openai_engine, "OpenAI", FakeClient)

    r = openai_engine.extract(str(img), ["Nabiał", "Napoje"])
    assert r["shop"] == "Lidl"
    assert r["date"] == date(2026, 11, 16)
    assert r["items"][1]["price"] == Decimal("7.49")
    assert r["items"][1]["category"] == "Napoje"
