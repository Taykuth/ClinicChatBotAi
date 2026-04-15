# 🦷 Klinik AI Chatbot

A lightweight, production-ready AI chatbot MVP for dental and aesthetic clinics. Built with FastAPI and OpenAI's GPT-4o-mini, it provides a 24/7 Turkish-speaking virtual assistant that handles patient inquiries about services, pricing, hours, and appointments.

**Live demo assistant:** *Gülüş Estetik Kliniği* — a fictional dental/aesthetic clinic used as the reference implementation.

---

## ✨ Features

- **WhatsApp-style chat UI** — familiar, mobile-first interface patients already know
- **Turkish-first conversational AI** — warm, professional tone tuned for clinic customer service
- **Context-aware** — remembers the last 6 messages for coherent multi-turn dialogue
- **Clinic knowledge baked in** — services, prices, hours, address, and WhatsApp line are part of the system prompt, so answers are always accurate
- **Zero frontend dependencies** — single HTML file, pure CSS and vanilla JS
- **Typing indicator** — "Yazıyor..." feedback while the model responds
- **Smart routing** — appointment requests are directed to the clinic's WhatsApp line
- **Safe by design** — the assistant never provides medical diagnoses and recommends an in-person visit for clinical concerns
- **Deploy-ready** — works out of the box on Render, Railway, Fly.io, or any Python host

---

## 🛠️ Tech Stack

| Layer     | Technology                        |
|-----------|-----------------------------------|
| Backend   | Python 3.11 + FastAPI + Uvicorn   |
| AI        | OpenAI API (`gpt-4o-mini`)        |
| Frontend  | Single-file HTML / CSS / JS       |
| Hosting   | Render / Railway / Fly.io ready   |

---

## 📁 Project Structure

```
klinik-chatbot/
├── main.py              # FastAPI app + chat endpoint
├── requirements.txt     # Python dependencies
├── Procfile             # Process definition for PaaS deploys
├── .env.example         # Template for environment variables
├── .gitignore
└── static/
    └── index.html       # Chat UI (self-contained)
```

---

## 🚀 Quick Start (Local)

### 1. Clone the repo
```bash
git clone https://github.com/Taykuth/ClinicChatBotAi.git
cd ClinicChatBotAi
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure your API key
Copy the example env file and add your OpenAI API key:
```bash
cp .env.example .env
```
Then edit `.env`:
```
OPENAI_API_KEY=sk-proj-your-key-here
```

Get an API key at [platform.openai.com/api-keys](https://platform.openai.com/api-keys).

### 4. Run the server
```bash
uvicorn main:app --reload
```

### 5. Open the chat
Visit [http://localhost:8000](http://localhost:8000) and start chatting.

---

## ☁️ Deploying to Render (Free)

1. Push this repo to GitHub (already done if you cloned).
2. Go to [render.com](https://render.com) → **New +** → **Web Service**.
3. Connect your GitHub and select the repo.
4. Configure:
   - **Runtime:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Instance Type:** Free
5. Under **Environment Variables**, add:
   - `OPENAI_API_KEY` = *your key*
6. Click **Create Web Service**.

Your chatbot will be live at `https://your-service.onrender.com` in a few minutes.

> **Note:** Render's free tier sleeps after 15 minutes of inactivity. The first request after sleep takes ~30 seconds to wake up. This is fine for demos; upgrade to a paid tier for production.

---

## 🔌 API Reference

### `POST /chat`

**Request body:**
```json
{
  "message": "Botoks ne kadar?",
  "history": [
    {"role": "user", "content": "Merhaba"},
    {"role": "assistant", "content": "Merhaba! Size nasıl yardımcı olabilirim?"}
  ]
}
```

**Response:**
```json
{
  "reply": "Botoks fiyatımız ₺3000. Randevu için WhatsApp'tan bize yazabilirsiniz: 0532 000 00 00"
}
```

Only the last 6 messages of `history` are passed to the model to keep token usage predictable.

---

## 🎨 Customizing for Your Clinic

To adapt this chatbot for a real clinic, edit `main.py` and update the `SYSTEM_PROMPT` variable with:

- Clinic name, branding, and tone of voice
- Full service list and pricing
- Working hours
- Address and contact details (phone, WhatsApp, email)
- Any clinic-specific rules (e.g., payment methods, insurance acceptance, languages)

For visual branding, edit `static/index.html`:
- Change the header color (`#1a73e8`) to your brand color
- Replace the 🦷 emoji with your logo or a relevant icon
- Update the header title and tagline

No code changes are required beyond the system prompt and frontend strings.

---

## 💰 Cost Estimation

Using `gpt-4o-mini`:
- **Input:** $0.15 per 1M tokens
- **Output:** $0.60 per 1M tokens
- **Average message:** ~500 input + 200 output tokens ≈ **$0.0002**

A $5 balance handles roughly **20,000+ conversations** — more than enough for demos and small clinic traffic.

---

## 🔒 Security Notes

- Never commit your `.env` file — it's in `.gitignore` by default.
- For production, add rate limiting (per-IP and per-day) to prevent abuse of your OpenAI quota.
- Consider enabling OpenAI's usage limits in your dashboard to cap monthly spend.

---

## 📄 License

MIT — use it, fork it, sell it, deploy it for your clinic. Attribution appreciated but not required.

---

## 🙋 Author

Built by [Taykuth](https://github.com/Taykuth) as a production-ready MVP for small Turkish dental and aesthetic clinics looking to automate their first line of patient communication.
