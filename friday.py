import subprocess
import json
import re
from memory_manager import load_memory, save_memory, update_short_term

# Load base system prompt
BASE_SYSTEM_PROMPT = open("friday_prompt.txt", encoding="utf-8").read()

def load_personality():
    with open("friday_personality.json", "r") as f:
        return json.load(f)

def build_prompt(user_input, memory):
    personality = load_personality()
    humor_level = personality.get("humor_level", 0)

    system_prompt = BASE_SYSTEM_PROMPT.replace(
        "{humor_level}", str(humor_level)
    )

    memory_block = f"""
PROFILE: {memory['profile']}
LONG TERM MEMORY: {memory['long_term']}
SHORT TERM MEMORY: {memory['short_term']}
"""

    return f"{system_prompt}\n{memory_block}\nUser: {user_input}\nFRIDAY:"

def ask_friday(user_input):

    # 🎛 HUMOR CONTROL (TARS-style)
    if "set humor" in user_input.lower():
        match = re.search(r"\d+", user_input)
        if not match:
            return "Please specify a humor level between 0 and 100."

        value = max(0, min(100, int(match.group())))

        with open("friday_personality.json", "w") as f:
            json.dump({"humor_level": value}, f, indent=2)

        return f"Humor level set to {value}/100."

    memory = load_memory()
    prompt = build_prompt(user_input, memory)

    # ✅ CORRECT Ollama call
    process = subprocess.Popen(
        ["ollama", "run", "mistral"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="ignore"
    )

    stdout, stderr = process.communicate(prompt)

    reply = stdout.strip()

    if not reply:
        return "⚠️ FRIDAY received no response from the model."

    # 🧠 MEMORY INTELLIGENCE
    if "MEMORY_SAVE:" in reply:
        fact = reply.split("MEMORY_SAVE:")[1].strip()
        memory["long_term"].append(fact)
        update_short_term(memory, user_input, reply)
        save_memory(memory)
        reply = reply.split("MEMORY_SAVE:")[0].strip()

    return reply

# 🔁 MAIN LOOP
while True:
    user_input = input("🧠 You: ")
    if user_input.lower() in ["exit", "quit"]:
        break

    response = ask_friday(user_input)
    print("\n🤖 FRIDAY:", response)