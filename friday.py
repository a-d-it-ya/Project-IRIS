import subprocess
import json
import re
import requests
import os
from datetime import datetime
from memory_manager import load_memory, save_memory, update_short_term

# ==============================
# CONFIG
# ==============================
MODEL_NAME = "phi3:mini"
DEFAULT_CITY = "Kolkata"
WEATHER_API_KEY = "417b0a73e56434ec33e9630d7b3b882b"
NEWS_API_KEY = "1494fe4df5fa4415b4043703a4b26a9c"

# ==============================
# PATHS
# ==============================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROMPT_PATH = os.path.join(BASE_DIR, "friday_prompt.txt")
PERSONALITY_PATH = os.path.join(BASE_DIR, "friday_personality.json")

BASE_SYSTEM_PROMPT = open(PROMPT_PATH, encoding="utf-8").read()

# ==============================
# PERSONALITY
# ==============================
def load_personality():
    if not os.path.exists(PERSONALITY_PATH):
        with open(PERSONALITY_PATH, "w") as f:
            json.dump({"humor_level": 0}, f, indent=2)

    with open(PERSONALITY_PATH, "r") as f:
        return json.load(f)

# ==============================
# TIME / DATE (OFFLINE)
# ==============================
def get_time_context():
    now = datetime.now()
    return {
        "time": now.strftime("%H:%M"),
        "date": now.strftime("%Y-%m-%d"),
        "day": now.strftime("%A"),
    }

# ==============================
# WEATHER (ONLINE)
# ==============================
def get_weather(city=DEFAULT_CITY):
    try:
        url = (
            "https://api.openweathermap.org/data/2.5/weather"
            f"?q={city}&appid={WEATHER_API_KEY}&units=metric"
        )
        r = requests.get(url, timeout=5)
        if r.status_code != 200:
            return None

        data = r.json()
        return {
            "city": data.get("name", city),
            "temp": round(data["main"]["temp"]),
            "condition": data["weather"][0]["description"],
        }
    except Exception:
        return None

# ==============================
# NEWS (ONLINE)
# ==============================
def get_news(category="general", country="in", limit=5):
    try:
        # 1️⃣ Primary: country-based headlines
        url = "https://newsapi.org/v2/top-headlines"
        params = {
            "country": country,
            "category": category,
            "pageSize": limit,
            "apiKey": NEWS_API_KEY,
        }

        r = requests.get(url, params=params, timeout=5)
        data = r.json()

        articles = data.get("articles", [])

        # 2️⃣ Fallback: global keyword-based search
        if not articles:
            fallback_params = {
                "q": "technology OR world OR science",
                "language": "en",
                "pageSize": limit,
                "sortBy": "publishedAt",
                "apiKey": NEWS_API_KEY,
            }

            r = requests.get(
                "https://newsapi.org/v2/everything",
                params=fallback_params,
                timeout=5,
            )
            data = r.json()
            articles = data.get("articles", [])

        if not articles:
            print("[NEWS ERROR] No articles returned after fallback")
            return None

        headlines = []
        for a in articles:
            title = a.get("title")
            source = a.get("source", {}).get("name", "Unknown")
            if title:
                headlines.append(f"{title} ({source})")

        return headlines[:limit]

    except Exception as e:
        print("[NEWS EXCEPTION]", e)
        return None

# ==============================
# PROMPT BUILDER
# ==============================
def build_prompt(user_input, memory):
    personality = load_personality()
    humor_level = personality.get("humor_level", 0)

    t = get_time_context()
    w = get_weather()

    system_prompt = BASE_SYSTEM_PROMPT.replace("{humor_level}", str(humor_level))

    context = f"""
SYSTEM CONTEXT:
- Time: {t['time']}
- Date: {t['date']}
- Day: {t['day']}
"""

    if w:
        context += f"- Weather: {w['temp']}°C, {w['condition']} in {w['city']}\n"
    else:
        context += "- Weather: unavailable\n"

    memory_block = f"""
PROFILE: {memory['profile']}
LONG TERM MEMORY: {memory['long_term']}
SHORT TERM MEMORY: {memory['short_term']}
"""

    return f"""{system_prompt}
{context}
{memory_block}
User: {user_input}
FRIDAY:"""

# ==============================
# MAIN LOGIC
# ==============================
def ask_friday(user_input):
    text = user_input.lower()

    # 🎬 Wake phrases
    if any(p in text for p in ["wake up", "daddy's home", "im back", "i'm back", "hello friday"]):
        return "Welcome back, Boss. Systems online and nominal."

    # 🎛 Humor control
    if "set humor" in text:
        match = re.search(r"\d+", text)
        if not match:
            return "Specify a humor level between 0 and 100, Boss."

        value = max(0, min(100, int(match.group())))
        with open(PERSONALITY_PATH, "w") as f:
            json.dump({"humor_level": value}, f, indent=2)

        return f"Humor level set to {value}/100."

    # 🕒 Time
    if "time" in text:
        t = get_time_context()
        return f"It's {t['time']} on {t['day']}, Boss."

    # 📅 Date
    if "date" in text:
        t = get_time_context()
        return f"Today's date is {t['date']}, Boss."

    # 🌤 Weather
    if "weather" in text:
        w = get_weather()
        if not w:
            return "Weather data is unavailable right now, Boss."
        return f"{w['temp']}°C with {w['condition']} in {w['city']}, Boss."

    # 📰 NEWS — MUST BE BEFORE LLM
    # 📰 NEWS — HARD OVERRIDE (NO LLM FALLBACK)
    if "news" in text:
        category = "general"
        if any(k in text for k in ["tech", "ai", "technology"]):
            category = "technology"
        elif "business" in text:
            category = "business"
        elif any(k in text for k in ["science", "space"]):
            category = "science"

        news = get_news(category=category)

        if not news:
            return "News service is reachable, but no usable headlines were returned, Boss."

        response = "Here’s what’s making headlines right now, Boss:\n"
        for n in news:
            response += f"• {n}\n"

        return response.strip()

    # ==============================
    # LLM (LAST RESORT)
    # ==============================
    memory = load_memory()
    prompt = build_prompt(user_input, memory)

    process = subprocess.Popen(
        ["ollama", "run", MODEL_NAME],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="ignore",
    )

    stdout, _ = process.communicate(prompt)
    reply = stdout.strip()

    if not reply:
        return "No response from the model, Boss."

    # 🧠 MEMORY
    if "MEMORY_SAVE:" in reply:
        fact = reply.split("MEMORY_SAVE:")[1].strip()
        memory["long_term"].setdefault("facts", []).append(fact)
        update_short_term(memory, user_input, reply)
        save_memory(memory)
        reply = reply.split("MEMORY_SAVE:")[0].strip()

    return reply

# ==============================
# LOOP
# ==============================
while True:
    user_input = input("🧠 You: ")
    if user_input.lower() in ["exit", "quit"]:
        break

    print("\n🤖 FRIDAY:", ask_friday(user_input))