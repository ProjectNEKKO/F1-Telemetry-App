from PySide6.QtWidgets import QMainWindow, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget
from PySide6.QtGui import QColor

class MainWindow(QMainWindow):
  def __init__(self, results_df):
    super().__init__()
    self.setWindowTitle("F1 Race Results")

    table = QTableWidget()
    table.setRowCount(len(results_df))
    table.setColumnCount(len(results_df.columns))
    table.setHorizontalHeaderLabels(results_df.columns)

    for row_number, (_, row) in enumerate(results_df.iterrows()):
      team_color = QColor(row["TeamColor"]) if "TeamColor" in row else None

      for col_idx, value in enumerate(row):
        item = QTableWidgetItem(str(value))
        
        if team_color:
          item.setBackground(team_color)
          if self.is_dark_color(team_color):
            item.setForeground(QColor("#FFFFFF"))

          table.setItem(row_number, col_idx, item)

    layout = QVBoxLayout()
    layout.addWidget(table)

    container = QWidget()
    container.setLayout(layout)
    self.setCentralWidget(container)

  def is_dark_color(self, color):
    luminance = (0.299 * color.red() + 0.587 * color.green() + 0.114 * color.blue()) / 255
    return luminance < 0.5
