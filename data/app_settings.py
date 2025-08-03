import json
import os

SETTINGS_FILE = "settings.json"

def load_settings():
  if os.path.exists(SETTINGS_FILE):
    with open(SETTINGS_FILE, "r") as f:
      try:
        return json.load(f)
      except json.JSONDecodeError:
        return{}
  return{}

def save_settings(settings: dict):
  with open(SETTINGS_FILE, "w") as f:
    json.dump(settings, f)