import sys
from PySide6.QtWidgets import QApplication
from data.race_results import fetch_race_results
from ui.main_window import MainWindow

if __name__ == "__main__":
  app = QApplication(sys.argv)

  results = fetch_race_results(year=2024, round_number=1, session_type='R')

  window = MainWindow(results)
  window.resize(650, 550)
  window.show()

  sys.exit(app.exec())