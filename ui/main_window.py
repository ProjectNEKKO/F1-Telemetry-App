from PySide6.QtWidgets import QMainWindow, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget
from PySide6.QtGui import QColor, QFont

class MainWindow(QMainWindow):
  def __init__(self, results_df):
    super().__init__()
    self.setWindowTitle("F1 Race Results")

    if "TeamColor" in results_df.columns:
      self.team_colors = results_df["TeamColor"].tolist()
      results_df = results_df.drop(columns=["TeamColor"])
    else:
      self.team_colors = [None] * len(results_df)

    table = QTableWidget()
    table.setRowCount(len(results_df))
    table.setColumnCount(len(results_df.columns))
    table.setHorizontalHeaderLabels(results_df.columns)

    for row_number, (_, row) in enumerate(results_df.iterrows()):
      for col_idx, col_name in enumerate(results_df.columns):
        value = row[col_name]
        item = QTableWidgetItem(str(value))
        
        font = QFont()
        if col_name in ["TeamName", "Gap to Leader", "Gap to Next"]:
          font.setBold(True)

        if col_name == "TeamName" and self.team_colors[row_number]:
          team_color = QColor(self.team_colors[row_number])
          item.setForeground(team_color)
          
        item.setFont(font)
        table.setItem(row_number, col_idx, item)

    layout = QVBoxLayout()
    layout.addWidget(table)
    container = QWidget()
    container.setLayout(layout)
    self.setCentralWidget(container)
