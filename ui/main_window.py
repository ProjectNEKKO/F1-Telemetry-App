from PySide6.QtWidgets import QMainWindow, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget, QHeaderView
from PySide6.QtGui import QColor, QFont
from PySide6.QtCore import Qt

class MainWindow(QMainWindow):
  def __init__(self, results_df):
    super().__init__()
    self.setWindowTitle("F1 Race Results")
    self.resize(850, 600)
    self.setMinimumSize(750, 550)

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
        table.setItem(row_number, col_idx, item)

    header = table.horizontalHeader()
    header.setSectionResizeMode(QHeaderView.Stretch)

    header.setMinimumSectionSize(60)

    for col_idx, col_name in enumerate(results_df.columns):
      if col_name == "TeamName":
        table.setColumnWidth(col_idx, 140)  # Initial size
        header.resizeSection(col_idx, 140)
      elif col_name in ["Gap to Leader", "Gap to Next"]:
        table.setColumnWidth(col_idx, 100)
        header.resizeSection(col_idx, 100)

    table.resizeRowsToContents()
    
    layout = QVBoxLayout()
    layout.addWidget(table)
    container = QWidget()
    container.setLayout(layout)
    self.setCentralWidget(container)
