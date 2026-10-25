import json
import logging
import os
import time
from collections import defaultdict, deque
from pathlib import Path
from typing import Dict, List

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from openai import OpenAI
from pydantic import BaseModel

load_dotenv()
logger = logging.getLogger("clinic-chatbot")

BASE_DIR = Path(__file__).parent
CLINIC_FILE = Path(os.getenv("CLINIC_FILE", BASE_DIR / "clinic.json"))
MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

MAX_MESSAGE_CHARS = 1000
MAX_HISTORY_MESSAGES = 6
RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", "20"))
ALLOWED_HISTORY_ROLES = {"user", "assistant"}


def build_system_prompt(clinic: dict) -> str:
    services = "\n".join(f"- {s['name']}: ₺{s['price_try']}" for s in clinic["services"])
    hours = "\n".join(f"- {h}" for h in clinic["hours"])
    return f"""Sen "{clinic['name']}" adlı bir {clinic['type']}nin Türkçe konuşan, sıcak, profesyonel ve yardımsever müşteri asistanısın.

KLİNİK BİLGİLERİ:

Hizmetler ve Fiyatlar:
{services}

Çalışma Saatleri:
{hours}

Adres: {clinic['address']}
WhatsApp: {clinic['whatsapp']}

KURALLAR:
- Her zaman Türkçe cevap ver.
- Kısa, net ve samimi ol.
- Randevu talebi gelirse WhatsApp numarasına yönlendir.
- Fiyat sorularında tam liste yerine ilgili hizmetin fiyatını belirt.
- Yukarıdaki listede olmayan hizmet, fiyat veya bilgi uydurma; bilmiyorsan WhatsApp hattına yönlendir.
- Tıbbi teşhis koyma; ciddi durumlarda klinik ziyareti öner.
- Emoji kullanabilirsin (🦷✨😊) ama abartma."""


CLINIC = json.loads(CLINIC_FILE.read_text(encoding="utf-8"))
SYSTEM_PROMPT = build_system_prompt(CLINIC)

_client: OpenAI | None = None


def get_client() -> OpenAI:
    # Created on first use so the app (and its tests) can start without an API key.
    global _client
    if _client is None:
        _client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    return _client


def clean_history(history: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """Keep only user/assistant turns from the client, trimmed in count and length.

    The history comes from the browser, so it cannot be trusted: without this a
    caller could send a "system" message and override the clinic rules.
    """
    cleaned = []
    for item in history:
        role = item.get("role")
        content = item.get("content")
        if role in ALLOWED_HISTORY_ROLES and isinstance(content, str) and content.strip():
            cleaned.append({"role": role, "content": content[:MAX_MESSAGE_CHARS]})
    return cleaned[-MAX_HISTORY_MESSAGES:]


_requests: Dict[str, deque] = defaultdict(deque)


def rate_limited(client_ip: str) -> bool:
    """Simple in-memory sliding window per IP. Resets when the process restarts."""
    now = time.monotonic()
    window = _requests[client_ip]
    while window and now - window[0] > 60:
        window.popleft()
    if len(window) >= RATE_LIMIT_PER_MINUTE:
        return True
    window.append(now)
    return False


app = FastAPI(title=f"{CLINIC['name']} Chatbot")


class ChatRequest(BaseModel):
    message: str
    history: List[Dict[str, str]] = []


@app.post("/chat")
async def chat(req: ChatRequest, request: Request):
    client_ip = request.client.host if request.client else "unknown"
    if rate_limited(client_ip):
        return JSONResponse(
            status_code=429,
            content={"reply": "Çok fazla mesaj gönderdiniz. Lütfen bir dakika sonra tekrar deneyin."},
        )

    message = req.message.strip()
    if not message:
        return JSONResponse(status_code=400, content={"reply": "Lütfen bir mesaj yazın."})
    if len(message) > MAX_MESSAGE_CHARS:
        return JSONResponse(
            status_code=400,
            content={"reply": f"Mesajınız çok uzun. Lütfen {MAX_MESSAGE_CHARS} karakterden kısa yazın."},
        )

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(clean_history(req.history))
    messages.append({"role": "user", "content": message})

    try:
        resp = get_client().chat.completions.create(
            model=MODEL,
            messages=messages,
            max_tokens=300,
            temperature=0.7,
        )
        return {"reply": resp.choices[0].message.content}
    except Exception:
        # Log the details on the server; never show internal errors to patients.
        logger.exception("OpenAI request failed")
        return JSONResponse(
            status_code=502,
            content={"reply": "Üzgünüm, şu an yanıt veremiyorum. Lütfen biraz sonra tekrar deneyin."},
        )


app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")


@app.get("/")
async def root():
    return FileResponse(BASE_DIR / "static" / "index.html")
