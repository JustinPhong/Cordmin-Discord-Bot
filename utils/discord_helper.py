import os
import json

def load_json(filename="roles.json"):
    folder = "json"
    os.makedirs(folder, exist_ok=True)
    filepath = os.path.join(folder, filename)
    if not os.path.isfile(filepath):
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump({}, f, indent=4)
        return {}
    
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(data, filename="roles.json"):
    folder = "json"
    os.makedirs(folder, exist_ok=True)
    filepath = os.path.join(folder, filename)
    with open(filepath, "w") as f:
        json.dump(data, f, indent=4)

def remove_json(guild_id: str, role_id: int, filename="roles.json") -> bool:
    data = load_json(filename)
    if guild_id not in data:
        return False
    emoji_to_remove = None
    for emoji, stored_role_id in data[guild_id].items():
        if stored_role_id == role_id:
            emoji_to_remove = emoji
            break
    if not emoji_to_remove:
        return False
    del data[guild_id][emoji_to_remove]
    if not data[guild_id]:
        del data[guild_id]
    save_json(data, filename)
    return True