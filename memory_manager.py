import json

MEMORY_FILE = "memory.json"

def load_memory():
    with open(MEMORY_FILE, "r") as f:
        return json.load(f)

def save_memory(memory):
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=2)

def update_short_term(memory, user, assistant):
    memory["short_term"].append({
        "user": user,
        "assistant": assistant
    })
    memory["short_term"] = memory["short_term"][-5:]  # keep last 5 turns

def add_long_term(memory, fact):
    memory["long_term"].append(fact)
    
def add_long_term(memory, fact):
    if fact not in memory["long_term"]:
        memory["long_term"].append(fact)