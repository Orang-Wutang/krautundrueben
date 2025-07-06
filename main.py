import sys
import mysql.connector
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QTabWidget, QMainWindow
)

# Datenbankverbindung
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="krautundrueben"
    )

def test_db_connection():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM KUNDE")
        count = cursor.fetchone()[0]
        print(f"✔️ Verbindung erfolgreich! Es gibt {count} Kunden.")
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"❌ Fehler bei DB-Verbindung: {e}")

# Direkt mal testen:
test_db_connection()


class KundenTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.table = QTableWidget()
        layout.addWidget(self.table)
        self.setLayout(layout)
        self.lade_kunden()

    def lade_kunden(self):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT KUNDENNR, NACHNAME, VORNAME, EMAIL FROM KUNDE")
        daten = cursor.fetchall()

        self.table.setRowCount(len(daten))
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Kundennr.", "Nachname", "Vorname", "E-Mail"])

        for i, row in enumerate(daten):
            for j, value in enumerate(row):
                self.table.setItem(i, j, QTableWidgetItem(str(value)))

        cursor.close()
        conn.close()

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

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("krautundrueben Datenbank")
        self.resize(800, 600)

        tabs = QTabWidget()
        tabs.addTab(KundenTab(), "Kunden")
        tabs.addTab(BestellungenTab(), "Bestellungen")
        tabs.addTab(ZutatenTab(), "Zutaten")

        self.setCentralWidget(tabs)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
