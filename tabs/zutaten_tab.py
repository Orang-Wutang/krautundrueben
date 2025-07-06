# tabs/zutaten_tab.py
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem
from db import get_connection

class ZutatenTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.table = QTableWidget()
        layout.addWidget(self.table)
        self.setLayout(layout)
        self.lade_zutaten()

    def lade_zutaten(self):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT BEZEICHNUNG, BESTAND, EINHEIT, NETTOPREIS FROM ZUTAT")
        daten = cursor.fetchall()

        self.table.setRowCount(len(daten))
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Bezeichnung", "Bestand", "Einheit", "Nettopreis"])

        for i, row in enumerate(daten):
            for j, value in enumerate(row):
                self.table.setItem(i, j, QTableWidgetItem(str(value)))

        cursor.close()
        conn.close()
