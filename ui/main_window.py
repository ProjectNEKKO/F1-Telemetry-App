from PySide6.QtWidgets import QMainWindow, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget

class MainWindow(QMainWindow):
  def __init__(self, results_df):
    super().__init__()
    self.setWindowTitle("F1 Race Results")

    table = QTableWidget()
    table.setRowCount(len(results_df))
    table.setColumnCount(len(results_df.columns))
    table.setHorizontalHeaderLabels(results_df.columns)

    for row_number, (_, row) in enumerate(results_df.iterrows()):
      for col_idx, value in enumerate(row):
        table.setItem(row_number, col_idx, QTableWidgetItem(str(value)))

    layout = QVBoxLayout()
    layout.addWidget(table)

    container = QWidget()
    container.setLayout(layout)
    self.setCentralWidget(container)