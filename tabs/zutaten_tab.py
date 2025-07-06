# tabs/zutaten_tab.py
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem
from db import get_connection
from PyQt5.QtWidgets import QMessageBox

class ZutatenTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.table = QTableWidget()
        layout.addWidget(self.table)
        self.setLayout(layout)
        self.lade_zutaten()
        self.table.itemChanged.connect(self.bestand_aktualisieren)

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

    def bestand_aktualisieren(self, item):
        spalte = item.column()
        if spalte != 1:  # Nur "Bestand"-Spalte (Index 1) darf geändert werden
            return

        zeile = item.row()
        bezeichnung = self.table.item(zeile, 0).text()
        neuer_bestand = item.text()

        # Prüfen ob Zahl
        try:
            neuer_bestand = float(neuer_bestand)
        except ValueError:
            QMessageBox.warning(self, "Ungültiger Wert", "Bitte gib eine gültige Zahl für den Bestand ein.")
            self.lade_zutaten()
            return

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
                       UPDATE ZUTAT
                       SET BESTAND = %s
                       WHERE BEZEICHNUNG = %s
                       """, (neuer_bestand, bezeichnung))
        conn.commit()
        cursor.close()
        conn.close()
