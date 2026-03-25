---
title: Central Bank AI
emoji: 🏦
colorFrom: blue
colorTo: indigo
sdk: streamlit
sdk_version: 1.54.0
app_file: app.py
pinned: false
license: mit
---
# 🏦 Central Bank AI — BankBot

A professional AI-powered banking assistant built with Streamlit.

## Features

- 💬 Banking chatbot powered by **Groq AI** (cloud) or **Ollama** (local)
- 📊 Financial dashboard with transaction history and analytics
- 🔐 User authentication with session management
- 📋 FAQ-based instant responses from a structured intents database

## AI Backend

- **Cloud (HF Spaces):** Uses [Groq AI](https://console.groq.com) — set `GROQ_API_KEY` as a Space Secret
- **Local:** Falls back to [Ollama](https://ollama.com) (llama3) automatically

## Setup (Local)

```bash
pip install -r requirements.txt
ollama pull llama3
streamlit run app.py
```

## Setup (Hugging Face Spaces)

1. Add `GROQ_API_KEY` as a **Secret** in Space Settings
2. The app will automatically use Groq AI
