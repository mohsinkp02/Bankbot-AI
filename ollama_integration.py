import os
import requests
import json
import time

# Auto-detect backend: Groq if API key is set, otherwise Ollama
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
USE_GROQ = bool(GROQ_API_KEY)

BANKING_KEYWORDS = [
    "account", "loan", "card", "balance",
    "transfer", "bank", "interest", "emi",
    "credit", "debit", "kyc", "upi", "cheque",
    "deposit", "fd", "rd", "branch", "ifsc",
    "transaction", "payment", "savings", "checking",
    "mortgage", "investment", "fintech", "wallet",
    "rate", "rates", "support", "customer", "care",
    "help", "contact", "helpline", "number", "call",
    "document", "required", "identity", "proof", "open"
]

SYSTEM_PROMPT = """You are BankBot, a professional banking assistant.
You ONLY answer banking-related questions.
If the question is not related to banking, politely refuse.
Never answer questions about politics, sports, entertainment, coding, or personal advice.
Please provide clear, professional, and helpful responses."""


def is_banking_query(user_input):
    input_lower = user_input.lower()
    return any(word in input_lower for word in BANKING_KEYWORDS)


def get_active_backend():
    """Returns 'groq' if GROQ_API_KEY is set, otherwise 'ollama'."""
    return "groq" if USE_GROQ else "ollama"


# ─── Groq AI Functions ────────────────────────────────────────────────────────

def get_groq_response(prompt, history=None, model="llama-3.3-70b-versatile"):
    """Fetches a response from Groq AI API."""
    try:
        from groq import Groq
        client = Groq(api_key=GROQ_API_KEY)

        messages = [{"role": "system", "content": SYSTEM_PROMPT}]

        if history:
            for msg in history[-5:]:
                if msg.get("role") and msg.get("content"):
                    messages.append({"role": msg["role"], "content": msg["content"]})

        messages.append({"role": "user", "content": prompt})

        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.1,
            max_tokens=1000,
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Groq Error: {e}")
        return None


def stream_groq_response(prompt, history=None, model="llama-3.3-70b-versatile"):
    """Yields streamed response chunks from Groq AI API."""
    try:
        from groq import Groq
        client = Groq(api_key=GROQ_API_KEY)

        messages = [{"role": "system", "content": SYSTEM_PROMPT}]

        if history:
            for msg in history[-5:]:
                if msg.get("role") and msg.get("content"):
                    messages.append({"role": msg["role"], "content": msg["content"]})

        messages.append({"role": "user", "content": prompt})

        stream = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.1,
            max_tokens=1000,
            stream=True,
        )
        for chunk in stream:
            content = chunk.choices[0].delta.content
            if content:
                yield content
    except Exception as e:
        print(f"Groq Stream Error: {e}")
        yield None


# ─── Ollama Functions ─────────────────────────────────────────────────────────

def get_ollama_response(prompt, history=None, model="llama3:latest"):
    """Fetches a response from a local Ollama instance."""
    url = "http://127.0.0.1:11434/api/chat"
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    if history:
        for msg in history[-5:]:
            if msg.get("role") and msg.get("content"):
                messages.append({"role": msg["role"], "content": msg["content"]})

    messages.append({"role": "user", "content": prompt})

    payload = {
        "model": model,
        "messages": messages,
        "stream": False,
        "options": {"temperature": 0.1, "top_p": 0.9, "num_predict": 1000}
    }

    try:
        response = requests.post(url, json=payload, timeout=90)
        response.raise_for_status()
        data = response.json()
        return data.get("message", {}).get("content", "")
    except Exception as e:
        print(f"Ollama Error: {e}")
        if model == "llama3:latest":
            return get_ollama_response(prompt, history, model="llama3")
        return None


def stream_ollama_response(prompt, history=None, model="llama3:latest"):
    """Yields chunks of the response from a local Ollama instance for streaming."""
    url = "http://127.0.0.1:11434/api/chat"
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    if history:
        for msg in history[-5:]:
            if msg.get("role") and msg.get("content"):
                messages.append({"role": msg["role"], "content": msg["content"]})

    messages.append({"role": "user", "content": prompt})

    payload = {
        "model": model,
        "messages": messages,
        "stream": True,
        "options": {"temperature": 0.1, "top_p": 0.9, "num_predict": 1000}
    }

    try:
        response = requests.post(url, json=payload, timeout=90, stream=True)
        response.raise_for_status()

        for line in response.iter_lines():
            if line:
                chunk = json.loads(line)
                if 'message' in chunk and 'content' in chunk['message']:
                    yield chunk['message']['content']
                if chunk.get('done'):
                    break
    except Exception as e:
        print(f"Ollama Stream Error: {e}")
        if model == "llama3:latest":
            yield from stream_ollama_response(prompt, history, model="llama3")
        else:
            yield None


# ─── Unified Wrapper Functions ────────────────────────────────────────────────

def get_ai_response(prompt, history=None):
    """Auto-selects Groq or Ollama based on environment."""
    if USE_GROQ:
        return get_groq_response(prompt, history)
    return get_ollama_response(prompt, history)


def stream_ai_response(prompt, history=None):
    """Auto-selects streaming from Groq or Ollama based on environment."""
    if USE_GROQ:
        yield from stream_groq_response(prompt, history)
    else:
        yield from stream_ollama_response(prompt, history)


def check_ollama_connection():
    """Checks if the local Ollama server is running."""
    if USE_GROQ:
        return True
    try:
        response = requests.get("http://127.0.0.1:11434/", timeout=2)
        return response.status_code == 200
    except:
        return False
