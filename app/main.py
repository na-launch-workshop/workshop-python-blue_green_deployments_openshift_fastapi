from __future__ import annotations

import json
import os
from pathlib import Path

from typing import Dict

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import JSONResponse

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
GREETINGS_PATH = BASE_DIR / "data" / "greetings.json"
DEFAULT_COUNTRY_CODE = "EN"


def _load_greetings() -> Dict[str, str]:
    try:
        return json.loads(GREETINGS_PATH.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:  # pragma: no cover - fatal misconfiguration
        raise RuntimeError(f"Missing greetings data file at {GREETINGS_PATH}") from exc


def _country_code() -> str:
    code = os.getenv("COUNTRY_CODE", DEFAULT_COUNTRY_CODE)
    code = code.strip().upper()
    return code or DEFAULT_COUNTRY_CODE


app = FastAPI(title="Hello Country Service", version="1.0.0")
_greetings = _load_greetings()


@app.get("/")
async def read_root():
    country_code = _country_code()
    greeting = _greetings.get(country_code)

    if greeting is None:
        return JSONResponse(
            status_code=404,
            content={"error": f"Unknown country code '{country_code}'"},
        )

    return {"code": country_code, "message": greeting}
