from PySide6.QtWidgets import (
  QMainWindow, QTableWidget, QTableWidgetItem, QVBoxLayout,
  QWidget, QHeaderView, QHBoxLayout, QLabel, QPushButton, QComboBox
)
from PySide6.QtGui import QColor, QFont
from PySide6.QtCore import Qt

from data.race_results import fetch_race_results
from data.qualifying_results import fetch_qualifying_results
from data.schedule import get_race_schedule

import datetime
import pandas as pd


class MainWindow(QMainWindow):
  def __init__(self):
    super().__init__()
    self.setWindowTitle("F1 Race Results")
    self.resize(850, 600)
    self.setMinimumSize(750, 550)

    self.year_dropdown = QComboBox()
    current_year = datetime.datetime.now().year
    self.year_dropdown.addItems([str(y) for y in range(2018, current_year + 1)])
    self.year_dropdown.currentTextChanged.connect(self.update_gp_dropdown)

    self.gp_dropdown = QComboBox()
    self.update_gp_dropdown(self.year_dropdown.currentText())  # initial

    self.session_dropdown = QComboBox()
    self.session_dropdown.addItems(["R", "Q", "FP1", "FP2", "FP3"])

    load_button = QPushButton("Load")
    load_button.clicked.connect(self.load_results)

    controls_layout = QHBoxLayout()
    controls_layout.addWidget(QLabel("Year:"))
    controls_layout.addWidget(self.year_dropdown)
    controls_layout.addWidget(QLabel("Grand Prix:"))
    controls_layout.addWidget(self.gp_dropdown)
    controls_layout.addWidget(QLabel("Session:"))
    controls_layout.addWidget(self.session_dropdown)
    controls_layout.addWidget(load_button)

    self.table = QTableWidget()

    main_layout = QVBoxLayout()
    main_layout.addLayout(controls_layout)
    main_layout.addWidget(self.table)

    container = QWidget()
    container.setLayout(main_layout)
    self.setCentralWidget(container)

    self.load_results()

  def update_gp_dropdown(self, year):
    self.gp_dropdown.clear()
    schedule = get_race_schedule(int(year))
    for rnd, name in schedule:
      self.gp_dropdown.addItem(f"{rnd} - {name}", rnd)

  def load_results(self):
    year = int(self.year_dropdown.currentText())
    round_number = int(self.gp_dropdown.currentData())  
    session_type = self.session_dropdown.currentText()

    if session_type == "R":
        results_df = fetch_race_results(year, round_number, session_type)
    elif session_type == "Q":
        results_df = fetch_qualifying_results(year, round_number)
    else:
        results_df = None

    if results_df is not None:
        self.update_table(results_df)

  def update_table(self, results_df):
    if "TeamColor" in results_df.columns:
        self.team_colors = results_df["TeamColor"].tolist()
        results_df = results_df.drop(columns=["TeamColor"])
    else:
        self.team_colors = [None] * len(results_df)

    self.table.clear()
    self.table.setRowCount(len(results_df))
    self.table.setColumnCount(len(results_df.columns))
    self.table.setHorizontalHeaderLabels(results_df.columns)

    for row_number, (_, row) in enumerate(results_df.iterrows()):
        for col_idx, col_name in enumerate(results_df.columns):
            value = row[col_name]
            item = QTableWidgetItem(str(value))

            if col_name == "Best Lap":
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
                if self.team_colors[row_number]:
                    item.setForeground(QColor(self.team_colors[row_number]))
                item.setTextAlignment(Qt.AlignVCenter | Qt.AlignLeft)
            elif col_name in ["Gap to Leader", "Gap to Next"]:
                font.setBold(True)
                item.setTextAlignment(Qt.AlignVCenter | Qt.AlignLeft)
            else:
                item.setTextAlignment(Qt.AlignVCenter | Qt.AlignCenter)

            item.setFont(font)
            self.table.setItem(row_number, col_idx, item)

    header = self.table.horizontalHeader()
    header.setSectionResizeMode(QHeaderView.Stretch)
    header.setMinimumSectionSize(60)

    for col_idx, col_name in enumerate(results_df.columns):
        if col_name == "TeamName":
            self.table.setColumnWidth(col_idx, 140)
            header.resizeSection(col_idx, 140)
        elif col_name in ["Gap to Leader", "Gap to Next"]:
            self.table.setColumnWidth(col_idx, 100)
            header.resizeSection(col_idx, 100)

    self.table.resizeRowsToContents()