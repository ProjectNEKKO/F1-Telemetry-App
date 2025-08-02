import fastf1
import os

def get_race_schedule(year):
  os.makedirs("cache", exist_ok=True)
  fastf1.Cache.enable_cache("cache")

  schedule = fastf1.get_event_schedule(year)
  races = schedule[schedule['EventFormat'] != 'testing']  

  return [(int(row.RoundNumber), row.EventName) for _, row in races.iterrows()]
