import os
import fastf1

def fetch_qualifying_results(year=2024, round_number=1):
  os.makedirs("cache", exist_ok=True)
  fastf1.Cache.enable_cache("cache")

  session = fastf1.get_session(year, round_number, 'Q')
  session.load()

  results = session.results[['Position', 'Abbreviation', 'TeamName', 'Status']].copy()
  results = results.drop_duplicates(subset=['Abbreviation']).reset_index(drop=True)

  laps = session.laps
  best_lap_times = {}

  for driver_code in results['Abbreviation']:
    driver_laps = laps.pick_drivers(driver_code)
    if not driver_laps.empty:
      fastest = driver_laps['LapTime'].min()
      best_lap_times[driver_code] = fastest
    else:
      best_lap_times[driver_code] = None

  results['Best Lap'] = results['Abbreviation'].map(best_lap_times)

  leader_best = results.iloc[0]['Best Lap']
  gap_to_leader = []
  gap_to_next = []

  for idx in range(len(results)):
    current_best = results.iloc[idx]['Best Lap']

    if idx == 0:
      gap_to_leader.append("Leader")
    elif current_best is None:
      gap_to_leader.append("—")
    else:
      gap_to_leader.append(f"+{(current_best - leader_best).total_seconds():.3f}s")

    if idx == 0:
      gap_to_next.append("—")
    else:
      prev_best = results.iloc[idx - 1]['Best Lap']
      if current_best is None or prev_best is None:
        gap_to_next.append("—")
      else:
        gap_to_next.append(f"+{(current_best - prev_best).total_seconds():.3f}s")

  results['Gap to Leader'] = gap_to_leader
  results['Gap to Next'] = gap_to_next

  return results
