# data/free_practice_results.py
import os
import fastf1
import pandas as pd

def fetch_free_practice_results(year=2024, round_number=1, session_type='FP1'):
  os.makedirs("cache", exist_ok=True)
  fastf1.Cache.enable_cache("cache")

  session = fastf1.get_session(year, round_number, session_type)
  session.load()

  results = session.results[['Position', 'Abbreviation', 'TeamName']].copy()
  results = results.drop_duplicates(subset=['Abbreviation']).reset_index(drop=True)

  laps = session.laps
  best_lap_times = {}

  for driver_code in results['Abbreviation']:
    driver_laps = laps.pick_drivers([driver_code])
    if not driver_laps.empty:
      fastest = driver_laps['LapTime'].min()
      best_lap_times[driver_code] = fastest
    else:
      best_lap_times[driver_code] = None

    team_color_hex = session.get_driver(driver_code)['TeamColor']
    results.loc[results['Abbreviation'] == driver_code, 'TeamColor'] = f"#{team_color_hex}"

  results['Best Lap'] = results['Abbreviation'].map(best_lap_times)

  results = results.sort_values(by='Best Lap', na_position='last').reset_index(drop=True)
  results['Position'] = results.index + 1

  leader_best = results.iloc[0]['Best Lap']
  gap_to_leader = []
  gap_to_next = []

  for idx in range(len(results)):
    current_best = results.iloc[idx]['Best Lap']

    if idx == 0:
      gap_to_leader.append("Leader")
    elif pd.isna(current_best):
      gap_to_leader.append("—")
    else:
      gap_to_leader.append(f"+{(current_best - leader_best).total_seconds():.3f}s")

    if idx == 0:
            gap_to_next.append("—")
    else:
      prev_best = results.iloc[idx - 1]['Best Lap']
      if pd.isna(current_best) or pd.isna(prev_best):
        gap_to_next.append("—")
      else:
        gap_to_next.append(f"+{(current_best - prev_best).total_seconds():.3f}s")

  results['Gap to Leader'] = gap_to_leader
  results['Gap to Next'] = gap_to_next

  return results
