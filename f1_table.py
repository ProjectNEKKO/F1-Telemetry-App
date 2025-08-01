import sys
import os
import pandas as pd
from PySide6.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget
import fastf1

# --- Load F1 data ---
os.makedirs("cache", exist_ok=True)
fastf1.Cache.enable_cache("cache")

session = fastf1.get_session(2024, 1, 'R')  # Bahrain GP 2024 Race
session.load()

# Get results table
results = session.results[['Position', 'Abbreviation', 'Status']].copy()
laps = session.laps

# Leader details
leader_code = results.iloc[0]['Abbreviation']
leader_laps = laps.pick_driver(leader_code)
leader_laps_completed = leader_laps.shape[0]
leader_time_total = leader_laps['LapTime'].sum()

gap_to_leader = []
gap_to_next = []

for idx in range(len(results)):
    driver_code = results.iloc[idx]['Abbreviation']
    driver_status = results.iloc[idx]['Status']
    driver_laps = laps.pick_driver(driver_code)
    driver_laps_completed = driver_laps.shape[0]

    # Handle DNFs
    if driver_status not in ["Finished", "Lapped"] or driver_laps.empty:
        gap_to_leader.append("DNF")
        gap_to_next.append("DNF")
        continue

    driver_total_time = driver_laps['LapTime'].sum()

    # --- GAP TO LEADER ---
    if idx == 0:
        gap_to_leader.append("Leader")
    else:
        if driver_laps_completed < leader_laps_completed:
            laps_down = leader_laps_completed - driver_laps_completed
            gap_to_leader.append(f"+{laps_down} LAP{'S' if laps_down > 1 else ''}")
        else:
            gap = driver_total_time - leader_time_total
            gap_to_leader.append(f"+{gap.total_seconds():.3f}s")

    # --- GAP TO NEXT ---
    if idx == 0:
        gap_to_next.append("—")
    else:
        prev_code = results.iloc[idx - 1]['Abbreviation']
        prev_laps = laps.pick_driver(prev_code)
        prev_laps_completed = prev_laps.shape[0]

        if driver_laps_completed < prev_laps_completed:
            # This driver is a lap down compared to the car ahead
            laps_down = prev_laps_completed - driver_laps_completed
            gap_to_next.append(f"+{laps_down} LAP{'S' if laps_down > 1 else ''}")
        elif driver_laps_completed == prev_laps_completed:
            # Same lap → real time gap
            prev_total_time = prev_laps['LapTime'].sum()
            gap_next = abs(driver_total_time - prev_total_time)
            gap_to_next.append(f"+{gap_next.total_seconds():.3f}s")
        else:
            # This driver actually did more laps than the car ahead (very rare)
            gap_to_next.append("—")

# Add to DataFrame
results['Gap to Leader'] = gap_to_leader
results['Gap to Next'] = gap_to_next

# --- PySide6 GUI ---
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("F1 Race Results")

        table = QTableWidget()
        table.setRowCount(len(results))
        table.setColumnCount(len(results.columns))
        table.setHorizontalHeaderLabels(results.columns)

        for row_number, (_, row) in enumerate(results.iterrows()):
            for col_idx, value in enumerate(row):
                table.setItem(row_number, col_idx, QTableWidgetItem(str(value)))

        layout = QVBoxLayout()
        layout.addWidget(table)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.resize(650, 400)
    window.show()
    sys.exit(app.exec())
