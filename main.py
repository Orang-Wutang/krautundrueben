import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget

from db import get_connection
from tabs.kunden_tab import KundenTab
from tabs.bestellungen_tab import BestellungenTab
from tabs.zutaten_tab import ZutatenTab

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

test_db_connection()

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