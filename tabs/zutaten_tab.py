# tabs/zutaten_tab.py
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QLineEdit, QMessageBox

from db import get_connection


class ZutatenTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        self.suchfeld: QLineEdit = QLineEdit()
        self.suchfeld.setPlaceholderText("🔍 Zutaten suchen nach Bezeichnung oder Einheit")
        self.suchfeld.textChanged.connect(self.zutaten_filtern)
        layout.addWidget(self.suchfeld)

        self.table: QTableWidget = QTableWidget()
        layout.addWidget(self.table)

        self.setLayout(layout)
        self.lade_zutaten()

        self.table.itemChanged.connect(self.bestand_aktualisieren)

    def zutaten_filtern(self):
        suchtext = self.suchfeld.text().lower()

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT BEZEICHNUNG, BESTAND, EINHEIT, NETTOPREIS FROM ZUTAT")
        daten = cursor.fetchall()
        cursor.close()
        conn.close()

        gefiltert = [
            row for row in daten
            if suchtext in str(row[0]).lower()  # Bezeichnung
               or suchtext in str(row[2]).lower()  # Einheit
        ]

        self.table.setRowCount(len(gefiltert))
        for i, row in enumerate(gefiltert):
            for j, value in enumerate(row):
                self.table.setItem(i, j, QTableWidgetItem(str(value)))

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
        for i in range(self.table.columnCount()):
            self.table.setColumnWidth(i, 200)

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
