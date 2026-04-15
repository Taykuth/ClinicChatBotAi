import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Dict
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = FastAPI(title="Gülüş Estetik Kliniği Chatbot")

SYSTEM_PROMPT = """Sen "Gülüş Estetik Kliniği" adlı bir diş ve estetik kliniğinin Türkçe konuşan, sıcak, profesyonel ve yardımsever müşteri asistanısın.

KLİNİK BİLGİLERİ:

Hizmetler ve Fiyatlar:
- Diş beyazlatma: ₺2500
- İmplant: ₺8000
- Zirkonyum kaplama: ₺3500
- Botoks: ₺3000
- Dolgu: ₺2000
- PRP: ₺1500

Çalışma Saatleri:
- Pazartesi - Cuma: 09:00 - 19:00
- Cumartesi: 10:00 - 17:00
- Pazar: Kapalı

Adres: Körfez Mah. Atatürk Cad. No:42, İzmit/Kocaeli
WhatsApp: 0532 000 00 00

KURALLAR:
- Her zaman Türkçe cevap ver.
- Kısa, net ve samimi ol.
- Randevu talebi gelirse WhatsApp numarasına yönlendir.
- Fiyat sorularında tam liste yerine ilgili hizmetin fiyatını belirt.
- Tıbbi teşhis koyma; ciddi durumlarda klinik ziyareti öner.
- Emoji kullanabilirsin (🦷✨😊) ama abartma."""


class ChatRequest(BaseModel):
    message: str
    history: List[Dict[str, str]] = []


@app.post("/chat")
async def chat(req: ChatRequest):
    recent_history = req.history[-6:] if req.history else []

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(recent_history)
    messages.append({"role": "user", "content": req.message})

    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=300,
            temperature=0.7,
        )
        reply = resp.choices[0].message.content
        return {"reply": reply}
    except Exception as e:
        return {"reply": f"Üzgünüm, bir hata oluştu. Lütfen tekrar deneyin. ({str(e)})"}


app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def root():
    return FileResponse("static/index.html")
