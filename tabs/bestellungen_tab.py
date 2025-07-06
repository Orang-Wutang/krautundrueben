# tabs/bestellungen_tab.py
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem
from db import get_connection

class BestellungenTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.table = QTableWidget()
        layout.addWidget(self.table)
        self.setLayout(layout)
        self.lade_bestellungen()

    def lade_bestellungen(self):
        conn = get_connection()
        cursor = conn.cursor()
        query = """
            SELECT b.BESTELLNR, k.NACHNAME, b.BESTELLDATUM, b.RECHNUNGSBETRAG
            FROM BESTELLUNG b
            JOIN KUNDE k ON b.KUNDENNR = k.KUNDENNR
        """
        cursor.execute(query)
        daten = cursor.fetchall()

        self.table.setRowCount(len(daten))
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Bestellnr.", "Kunde", "Datum", "Betrag"])

        for i, row in enumerate(daten):
            for j, value in enumerate(row):
                self.table.setItem(i, j, QTableWidgetItem(str(value)))

        cursor.close()
        conn.close()
