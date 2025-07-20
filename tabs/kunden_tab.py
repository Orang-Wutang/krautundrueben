from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QLineEdit, QPushButton, QHBoxLayout
from db import get_connection

class KundenTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.setLayout(layout)

        #Suchfeld + Button
        such_layout = QHBoxLayout()
        self.suchfeld = QLineEdit()
        self.suchfeld.setPlaceholderText("Kundenname oder ID eingeben...")
        such_button = QPushButton("Suchen")
        such_button.clicked.connect(self.suche_kunden)

        such_layout.addWidget(self.suchfeld)
        such_layout.addWidget(such_button)
        layout.addLayout(such_layout)

        #Tabelle
        self.table = QTableWidget()
        layout.addWidget(self.table)

        self.load_data()

    def load_data(self):
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM KUNDEN")
        data = cursor.fetchall()
        self.table.setRowCount(len(data))
        self.zeige_daten_in_tabelle(data)
        if data:
            self.table.setColumnCount(len(data[0]))
            self.table.setHorizontalHeaderLabels(data[0].keys())
            for row_idx, row in enumerate(data):
                for col_idx, (key, value) in enumerate(row.items()):
                    self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))
        cursor.close()
        connection.close()

    def suche_kunden(self):
        suchtext = self.suchfeld.text().strip()
        connection = get_connection()
        cursor = connection.cursor()

        if suchtext:
            query = """
                SELECT * FROM KUNDEN
                WHERE VORNAME LIKE %s OR NACHNAME LIKE %s OR CAST(KUNDEN_ID AS CHAR) LIKE %s
            """
            like_text = f"%{suchtext}%"
            cursor.execute(query, (like_text, like_text, like_text))
        else:
            cursor.execute("SELECT * FROM KUNDEN")

        data = cursor.fetchall()
        self.zeige_daten_in_tabelle(data)
        cursor.close()
        connection.close()

    def zeige_daten_in_tabelle(self, data):
        self.table.clear()  # leere alte Daten
        self.table.setRowCount(len(data))

        if data:
            self.table.setColumnCount(len(data[0]))
            self.table.setHorizontalHeaderLabels(data[0].keys())
            for row_idx, row in enumerate(data):
                for col_idx, (key, value) in enumerate(row.items()):
                    self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))


