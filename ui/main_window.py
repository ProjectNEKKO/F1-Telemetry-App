from PySide6.QtWidgets import (
  QMainWindow, QTableWidget, QTableWidgetItem, QVBoxLayout,
  QWidget, QHeaderView, QHBoxLayout, QLabel, QPushButton, QComboBox, QTabWidget,

)
from PySide6.QtGui import (
  QColor, QFont, QIcon, QPixmap
)
from PySide6.QtCore import Qt

from data.race_results import fetch_race_results
from data.qualifying_results import fetch_qualifying_results
from data.free_practice_results import fetch_free_practice_results
from data.schedule import get_race_schedule
from data.app_settings import load_settings, save_settings

import fastf1

import datetime
import pandas as pd


class MainWindow(QMainWindow):
  def __init__(self):
    super().__init__()
    self.setWindowTitle("F1 Race Results")
    self.resize(1000, 580)
    self.setMinimumSize(900, 580)

    self.year_dropdown = QComboBox()
    current_year = datetime.datetime.now().year
    self.year_dropdown.addItems([str(y) for y in range(2018, current_year + 1)])
    self.year_dropdown.currentTextChanged.connect(self.update_gp_dropdown)

    self.gp_dropdown = QComboBox()
    self.update_gp_dropdown(self.year_dropdown.currentText())  

    self.session_dropdown = QComboBox()
    self.session_dropdown.addItems(["R", "Q", "FP1", "FP2", "FP3"])

    load_button = QPushButton("Load All Sessions")
    load_button.clicked.connect(self.load_all_sessions)

    controls_layout = QHBoxLayout()
    controls_layout.addWidget(QLabel("Year:"))
    controls_layout.addWidget(self.year_dropdown)
    controls_layout.addWidget(QLabel("Grand Prix:"))
    controls_layout.addWidget(self.gp_dropdown)
    controls_layout.addWidget(load_button)

    self.tabs = QTabWidget()
    self.tables = {}
    self.no_data_labels = {}
    for session in ["Race", "Qualifying", "FP3", "FP2", "FP1"]:
      table = QTableWidget()
      self.tables[session] = table

      label = QLabel("No data available")
      label.setAlignment(Qt.AlignCenter)
      label.setStyleSheet("font-size: 18px; font-weight: bold; color: white;")
      self.no_data_labels[session] = label

      self.tabs.addTab(table, session)

    settings = load_settings()
    if settings:
      self.year_dropdown.setCurrentText(str(settings.get("year", self.year_dropdown.currentText())))
      self.update_gp_dropdown(self.year_dropdown.currentText())

      saved_gp_name = settings.get("gp_name")
      if saved_gp_name:
        for i in range(self.gp_dropdown.count()):
          if saved_gp_name in self.gp_dropdown.itemText(i):
            self.gp_dropdown.setCurrentIndex(i)
            break
      
      self.tabs.setCurrentIndex(settings.get("tab_index", 0))

    self.load_all_sessions()

    main_layout = QVBoxLayout()
    main_layout.addLayout(controls_layout)
    main_layout.addWidget(self.tabs)

    container = QWidget()
    container.setLayout(main_layout)
    self.setCentralWidget(container)

  def update_gp_dropdown(self, year):
    self.gp_dropdown.clear()
    schedule = get_race_schedule(int(year))
    for rnd, name in schedule:
      self.gp_dropdown.addItem(f"{rnd} - {name}", rnd)

  def load_all_sessions(self):
    year = int(self.year_dropdown.currentText())
    round_number = int(self.gp_dropdown.currentData())  
    
    session_map = {
      "Race": ("R", fetch_race_results),
      "Qualifying": ("Q", fetch_qualifying_results),
      "FP1": ("FP1", fetch_free_practice_results),
      "FP2": ("FP2", fetch_free_practice_results),
      "FP3": ("FP3", fetch_free_practice_results),
    }

    for tab_name, (session_code, fetch_func) in session_map.items():
      try:
          if tab_name == "Race":
            df = fetch_func(year, round_number, session_code)
          elif tab_name == "Qualifying":
            df = fetch_func(year, round_number)
          else:
            df = fetch_func(year, round_number, session_code)

          if df is None or df.empty:
            self.show_no_data_message(tab_name, f"No {tab_name} for this GP")
          else:
            self.update_table(self.tables[tab_name], df)

      except Exception:
        self.show_no_data_message(tab_name, f"No {tab_name} for this GP")

  def show_no_data_message(self, tab_name, message):
    table = self.tables[tab_name]
    table.clear()
    table.setRowCount(1)
    table.setColumnCount(1)
    table.setHorizontalHeaderLabels(["Info"])
    item = QTableWidgetItem(message)
    item.setTextAlignment(Qt.AlignCenter)
    table.setItem(0, 0, item)

  def update_table(self, table_widget, results_df):
    session_name = [name for name, table in self.tables.items() if table is table_widget][0]

    if results_df is None or results_df.empty:
      tab_index = self.tabs.indexOf(table_widget)
      self.tabs.removeTab(tab_index)
      self.tabs.insertTab(tab_index, self.no_data_labels[session_name], session_name)
      return
    else:
      tab_index = self.tabs.indexOf(self.no_data_labels[session_name])
      if tab_index != -1:
        self.tabs.removeTab(tab_index)
        self.tabs.insertTab(tab_index, table_widget, session_name)


    if "TeamColor" in results_df.columns:
      self.team_colors = results_df["TeamColor"].tolist()
      results_df = results_df.drop(columns=["TeamColor"])
    else:
      self.team_colors = [None] * len(results_df)

    results_df = results_df.rename(columns={"Abbreviation": "Driver"})

    table_widget.clear()
    table_widget.setRowCount(len(results_df))
    table_widget.setColumnCount(len(results_df.columns))
    table_widget.setHorizontalHeaderLabels(results_df.columns)

    time_columns = {"Best Lap", "Q1", "Q2", "Q3"}

    for row_number, (_, row) in enumerate(results_df.iterrows()):
      for col_idx, col_name in enumerate(results_df.columns):
        value = row[col_name]
        item = QTableWidgetItem(str(value))

        if col_name in time_columns:
          if pd.notna(value):
            ms = int(value.microseconds / 1000)
            formatted = f"{value.seconds // 60}:{value.seconds % 60:02}.{ms:03}"
            item = QTableWidgetItem(formatted)
          else:
            item = QTableWidgetItem("—")
        else:
          item = QTableWidgetItem(str(value))

        font = QFont()
        if col_name == "TeamName":
          font.setBold(True)

          team_name = str(value).lower().replace(" ","_")
          logo_path = f"assets/team_logos/{team_name}.png"
          try:
            pixmap = QPixmap(logo_path)
            if not pixmap.isNull():
              icon = QIcon(pixmap)
              item.setIcon(icon)
          
          except:
            pass

          if self.team_colors[row_number]:
            item.setForeground(QColor(self.team_colors[row_number]))
          item.setTextAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        elif col_name in ["Gap to Leader", "Gap to Next"]:
          font.setBold(True)
          item.setTextAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        else:
          item.setTextAlignment(Qt.AlignVCenter | Qt.AlignCenter)

        item.setFont(font)
        table_widget.setItem(row_number, col_idx, item)

    header = table_widget.horizontalHeader()
    header.setSectionResizeMode(QHeaderView.Stretch)
    header.setMinimumSectionSize(60)
    table_widget.verticalHeader().setDefaultSectionSize(50)

    for col_idx, col_name in enumerate(results_df.columns):
      if col_name == "TeamName":
        table_widget.setColumnWidth(col_idx, 140)
        header.resizeSection(col_idx, 140)
      elif col_name in ["Gap to Leader", "Gap to Next"]:
        table_widget.setColumnWidth(col_idx, 100)
        header.resizeSection(col_idx, 100)

    table_widget.resizeRowsToContents()

  def closeEvent(self, event):
    settings = {
      "year": int(self.year_dropdown.currentText()),
      "gp_name": self.gp_dropdown.currentText(),
      "tab_index": self.tabs.currentIndex()
    }
    save_settings(settings)
    event.accept()