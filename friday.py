import subprocess
import json
import re
import requests
import os
import time
from datetime import datetime
from memory_manager import load_memory, save_memory, update_short_term

# ==============================
# CONFIG
# ==============================
MODEL_NAME = "phi3:mini"
DEFAULT_CITY = "Kolkata"
WEATHER_API_KEY = "417b0a73e56434ec33e9630d7b3b882b"

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
        "hour": now.hour
    }

# ==============================
# WEATHER (ONLINE + CACHE)
# ==============================
_weather_cache = None
_weather_cache_time = 0
WEATHER_CACHE_TTL = 600  # 10 minutes

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

        # Defensive checks
        if "main" not in data or "weather" not in data:
            return None

        if not data["weather"]:
            return None

        temp = data["main"].get("temp")
        condition = data["weather"][0].get("description")

        if temp is None or condition is None:
            return None

        return {
            "city": data.get("name", city),
            "temp": round(temp),
            "condition": condition
        }

    except requests.RequestException:
        return None

# ==============================
# PROMPT BUILDER
# ==============================
def build_prompt(user_input, memory):
    personality = load_personality()
    humor_level = personality.get("humor_level", 0)

    time_ctx = get_time_context()
    weather = get_weather()

    system_prompt = BASE_SYSTEM_PROMPT.replace(
        "{humor_level}", str(humor_level)
    )

    context_block = f"""
SYSTEM CONTEXT:
- Time: {time_ctx['time']}
- Date: {time_ctx['date']}
- Day: {time_ctx['day']}
"""

    if weather:
        context_block += f"- Weather: {weather['temp']}°C, {weather['condition']} in {weather['city']}\n"
    else:
        context_block += "- Weather: unavailable\n"

    memory_block = f"""
PROFILE: {memory['profile']}
LONG TERM MEMORY: {memory['long_term']}
SHORT TERM MEMORY: {memory['short_term']}
"""

    return f"""{system_prompt}
{context_block}
{memory_block}
User: {user_input}
FRIDAY:"""

# ==============================
# MAIN LOGIC
# ==============================
def ask_friday(user_input):
    lower = user_input.lower()

    # 🎬 Wake phrases
    if any(p in lower for p in ["wake up", "daddy's home", "im back", "i'm back", "hello friday"]):
        return "Welcome back, Boss. Systems online and nominal."

    # 🎛 Humor control
    if "set humor" in lower:
        match = re.search(r"\d+", lower)
        if not match:
            return "Specify a humor level between 0 and 100, Boss."

        value = max(0, min(100, int(match.group())))

        with open(PERSONALITY_PATH, "w") as f:
            json.dump({"humor_level": value}, f, indent=2)

        return f"Humor level set to {value}/100."

    # ⚡ Fast deterministic responses
    if "time" in lower:
        t = get_time_context()
        return f"It's {t['time']} on {t['day']}, Boss."

    if "date" in lower:
        t = get_time_context()
        return f"Today's date is {t['date']}, Boss."

    if "weather" in lower:
        w = get_weather()
        if not w:
            return "Weather data is unavailable right now, Boss."
        return f"{w['temp']}°C with {w['condition']} in {w['city']}, Boss."

    # ==============================
    # LLM CALL
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
        errors="ignore"
    )

    stdout, _ = process.communicate(prompt)
    reply = stdout.strip()

    if not reply:
        return "No response from the model, Boss."

    # ==============================
    # MEMORY HANDLING
    # ==============================
    if "MEMORY_SAVE:" in reply:
        fact = reply.split("MEMORY_SAVE:")[1].strip()

        if "facts" not in memory["long_term"]:
            memory["long_term"]["facts"] = []

        memory["long_term"]["facts"].append(fact)
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