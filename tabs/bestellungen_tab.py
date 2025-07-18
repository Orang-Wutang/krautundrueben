from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem
from db import get_connection

class BestellungenTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.table = QTableWidget()
        layout.addWidget(self.table)

        self.load_data()

    def load_data(self):
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM BESTELLUNGEN")
        data = cursor.fetchall()
        self.table.setRowCount(len(data))
        if data:
            self.table.setColumnCount(len(data[0]))
            self.table.setHorizontalHeaderLabels(data[0].keys())
            for row_idx, row in enumerate(data):
                for col_idx, (key, value) in enumerate(row.items()):
                    self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))
        cursor.close()
        connection.close()
