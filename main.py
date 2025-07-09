import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget
from db import get_sql_connection
from tabs.kunden_tab import KundenTab
from tabs.bestellungen_tab import BestellungenTab
from tabs.zutaten_tab import ZutatenTab
from pymongo import MongoClient

from pymongo import MongoClient

# Verbindung zu lokalem MongoDB-Server
client = MongoClient("mongodb://localhost:27017/")

# Datenbank "krautundrueben" auswählen
db = client["krautundrueben"]

# Collection "feedbacks" auswählen
feedbacks = db["feedbacks"]

# Testdokument einfügen
feedbacks.insert_one({
    "kunde_id": 1,
    "datum": "2025-07-09",
    "text": "Dies ist ein Testfeedback aus Python"
})

print("✅ Testfeedback gespeichert!")


def test_db_connection():
    try:
        conn = get_sql_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM KUNDE")
        count = cursor.fetchone()[0]
        print(f"✔️ Verbindung erfolgreich! Es gibt {count} Kunden.")
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"❌ Fehler bei DB-Verbindung: {e}")

test_db_connection()

class MainWindow(QMainWindow):
    def __init__(self):

        super().__init__()
        self.setWindowTitle("krautundrueben Datenbank")
        self.setMinimumSize(1000, 650)
        self.resize(1200, 750)
        self.center()
        self.setWindowTitle("🌸 krautundrueben Dashboard")

        tabs = QTabWidget()
        tabs.addTab(KundenTab(), "Kunden")
        tabs.addTab(BestellungenTab(), "Bestellungen")
        tabs.addTab(ZutatenTab(), "Zutaten")

        self.setCentralWidget(tabs)

    def center(self):
        frame_gm = self.frameGeometry()
        screen = self.screen().availableGeometry().center()
        frame_gm.moveCenter(screen)
        self.move(frame_gm.topLeft())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    # QSS-Datei laden
    with open("style.qss", "r") as f:
        app.setStyleSheet(f.read())
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())