import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget, QWidget

from tabs.bestellungen_tab import BestellungenTab
from tabs.kunden_tab import KundenTab
from tabs.lieferanten_tab import LieferantenTab
from tabs.rezepte_tab import  RezepteTab
from tabs.zutaten_tab import ZutatenTab


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Kraut und Rüben GUI")


        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        self.tabs.addTab(KundenTab(), "Kunden")
        self.tabs.addTab(BestellungenTab(), "Bestellungen")
        self.tabs.addTab(LieferantenTab(), "Lieferanten")
        self.tabs.addTab(RezepteTab(), "Rezepte")
        self.tabs.addTab(ZutatenTab(), "Zutaten")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
