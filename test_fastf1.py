import fastf1 
import fastf1.plotting
import pandas as pd

fastf1.Cache.enable_cache('cache')

year = 2024
round_number = 1
session_type = 'R'

print(f"Loading {year} Round {round_number} - {session_type},,,")
session = fastf1.get_session(year, round_number, session_type)
session.load()

print("\nDrivers in session:")
print(session.drivers)

# Example: Get session results
results = session.results
print("\nSession Results:")
print(results[['Abbreviation', 'Position', 'Time', 'Status']])

# Example: Get fastest lap data for one driver
driver_code = results.iloc[0]['Abbreviation']  # Leader
fastest_lap = session.laps.pick_driver(driver_code).pick_fastest()
print(f"\nFastest Lap for {driver_code}: {fastest_lap['LapTime']}")

# Example: Show telemetry for fastest lap
telemetry = fastest_lap.get_telemetry()
print("\nTelemetry columns available:")
print(telemetry.columns)

# Optional: Save telemetry to CSV for inspection
telemetry.to_csv(f"{driver_code}_fastest_lap.csv", index=False)
print(f"\nSaved telemetry for {driver_code} fastest lap to CSV.")