# tabs/kunden_tab.py
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QLineEdit, QDialog, QFormLayout, QDialogButtonBox
from db import get_connection

class KundenTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        self.add_button = QPushButton("➕ Neuen Kunden anlegen")
        self.add_button.clicked.connect(self.kunde_hinzufuegen_dialog)
        layout.addWidget(self.add_button)

        self.table = QTableWidget()
        layout.addWidget(self.table)

        self.setLayout(layout)
        self.lade_kunden()

    def kunde_hinzufuegen_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Neuer Kunde")

        form = QFormLayout(dialog)
        vorname = QLineEdit()
        nachname = QLineEdit()
        email = QLineEdit()
        form.addRow("Vorname:", vorname)
        form.addRow("Nachname:", nachname)
        form.addRow("E-Mail:", email)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        form.addWidget(buttons)

        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)

        if dialog.exec_() == QDialog.Accepted:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT MAX(KUNDENNR) FROM KUNDE")
            max_id = cursor.fetchone()[0] or 2000
            neue_id = max_id + 1
            cursor.execute(
                "INSERT INTO KUNDE (KUNDENNR, VORNAME, NACHNAME, EMAIL) VALUES (%s, %s, %s, %s)",
                (neue_id, vorname.text(), nachname.text(), email.text())
            )
            conn.commit()
            cursor.close()
            conn.close()
            self.lade_kunden()

    def lade_kunden(self):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT KUNDENNR, NACHNAME, VORNAME, EMAIL FROM KUNDE")
        daten = cursor.fetchall()

        self.table.setRowCount(len(daten))
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Kundennr", "Nachname", "Vorname", "E-Mail"])

        for i, row in enumerate(daten):
            for j, value in enumerate(row):
                self.table.setItem(i, j, QTableWidgetItem(str(value)))

        cursor.close()
        conn.close()

