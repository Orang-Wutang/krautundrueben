# tabs/kunden_tab.py
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QLineEdit, QDialog, QFormLayout, QDialogButtonBox
from db import get_connection
from PyQt5.QtWidgets import QMessageBox


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
        geburtstag = QLineEdit()  # Alternativ: QDateEdit()
        strasse = QLineEdit()
        hausnr = QLineEdit()
        plz = QLineEdit()
        ort = QLineEdit()
        telefon = QLineEdit()

        form.addRow("Vorname:", vorname)
        form.addRow("Nachname:", nachname)
        form.addRow("E-Mail:", email)
        form.addRow("Geburtsdatum (JJJJ-MM-TT):", geburtstag)
        form.addRow("Straße:", strasse)
        form.addRow("Hausnummer:", hausnr)
        form.addRow("PLZ:", plz)
        form.addRow("Ort:", ort)
        form.addRow("Telefon:", telefon)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        form.addWidget(buttons)

        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)

        def ist_gueltig(feld):
            return feld.text().strip() != ""

        if dialog.exec_() == QDialog.Accepted:
            felder = [vorname, nachname, email, geburtstag, strasse, hausnr, plz, ort, telefon]
            if not all(ist_gueltig(f) for f in felder):
                QMessageBox.warning(self, "Fehler", "Alle Felder müssen ausgefüllt sein (kein Leerzeichen).")
                return
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT MAX(KUNDENNR) FROM KUNDE")
            max_id = cursor.fetchone()[0] or 2000
            neue_id = max_id + 1
            cursor.execute("""
                           INSERT INTO KUNDE (KUNDENNR, VORNAME, NACHNAME, EMAIL, GEBURTSDATUM, STRASSE, HAUSNR,
                                              PLZ, ORT, TELEFON)
                           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                           """, (
                               neue_id,
                               vorname.text().strip(),
                               nachname.text().strip(),
                               email.text().strip(),
                               geburtstag.text().strip(),
                               strasse.text().strip(),
                               hausnr.text().strip(),
                               plz.text().strip(),
                               ort.text().strip(),
                               telefon.text().strip()
                           ))
            conn.commit()
            cursor.close()
            conn.close()
            self.lade_kunden()

    def lade_kunden(self):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
                       SELECT KUNDENNR,
                              VORNAME,
                              NACHNAME,
                              GEBURTSDATUM,
                              STRASSE,
                              HAUSNR,
                              PLZ,
                              ORT,
                              TELEFON,
                              EMAIL
                       FROM KUNDE
                       """)
        daten = cursor.fetchall()

        self.table.setRowCount(len(daten))
        self.table.setColumnCount(10)
        self.table.setHorizontalHeaderLabels([
            "Kundennr", "Vorname", "Nachname", "Geburtsdatum", "Straße", "Hausnr.",
            "PLZ", "Ort", "Telefon", "E-Mail"
        ])

        for i, row in enumerate(daten):
            for j, value in enumerate(row):
                self.table.setItem(i, j, QTableWidgetItem(str(value)))

        cursor.close()
        conn.close()

