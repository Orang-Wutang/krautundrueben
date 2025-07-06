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
        self.setFixedSize(1000, 700)
        self.center()

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