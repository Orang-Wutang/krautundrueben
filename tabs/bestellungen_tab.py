# tabs/bestellungen_tab.py
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QLineEdit
from db import get_connection

class BestellungenTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        self.suchfeld: QLineEdit = QLineEdit()
        self.suchfeld.setPlaceholderText("🔍 Bestellungen suchen nach Name oder Datum")
        self.suchfeld.textChanged.connect(self.bestellungen_filtern)
        layout.addWidget(self.suchfeld)

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

    def bestellungen_filtern(self):
        suchtext = self.suchfeld.text().lower()

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
                       SELECT b.BESTELLNR, k.NACHNAME, b.BESTELLDATUM, b.RECHNUNGSBETRAG
                       FROM BESTELLUNG b
                                JOIN KUNDE k ON b.KUNDENNR = k.KUNDENNR
                       """)
        daten = cursor.fetchall()
        cursor.close()
        conn.close()

        gefiltert = [
            row for row in daten
            if suchtext in str(row[1]).lower()  # Nachname
               or suchtext in str(row[2]).lower()  # Datum
        ]

        self.table.setRowCount(len(gefiltert))
        for i, row in enumerate(gefiltert):
            for j, value in enumerate(row):
                self.table.setItem(i, j, QTableWidgetItem(str(value)))

