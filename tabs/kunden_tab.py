# tabs/kunden_tab.py
import random

from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QDialog, QFormLayout, \
    QDialogButtonBox

from db import get_connection


class KundenTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        # Suchfeld
        self.suchfeld: QLineEdit = QLineEdit()
        self.suchfeld.setPlaceholderText("🔍 Kunden suchen nach Name, Vorname oder E-Mail")
        self.suchfeld.textChanged.connect(self.kunden_filtern)
        layout.addWidget(self.suchfeld)

        # Button zum Kunden hinzufügen
        self.add_button: QPushButton = QPushButton("➕ Neuen Kunden anlegen")
        self.add_button.clicked.connect(self.kunde_hinzufuegen_dialog)
        layout.addWidget(self.add_button)

        # Tabelle
        self.table: QTableWidget = QTableWidget()
        layout.addWidget(self.table)

        self.setLayout(layout)
        self.lade_kunden()

        self.delete_button: QPushButton = QPushButton("🗑️ Kunden löschen")
        self.delete_button.clicked.connect(self.kunde_loeschen)
        layout.addWidget(self.delete_button)

    def kunde_loeschen(self):
        selected_items = self.table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Keine Auswahl", "Bitte wähle einen Kunden aus, den du löschen möchtest.")
            return

        zeile = selected_items[0].row()
        kundennr = self.table.item(zeile, 0).text()

        # 1. Schritt: erste witzige Frage
        texte = [
            "Willst du diesen Kunden wirklich löschen? 😢",
            "Wirklich löschen? Vielleicht hat er einfach nur einen schlechten Tag gehabt 🤷‍♀️",
            "Das ist dein letzter Moment, um es dir anders zu überlegen… 🤔",
            "Der Kunde wird nie wieder gesehen werden. Bist du bereit für diese Verantwortung?",
            f"Kundennummer {kundennr}… war's das wirklich wert?"
        ]

        spruch = random.choice(texte)

        erste_frage = QMessageBox.question(
            self,
            "Letzte Chance 😬",
            spruch,
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if erste_frage != QMessageBox.Yes:
            return  # abgebrochen

        # 2. Schritt: Noch mal ganz sicher?
        zweite_frage = QMessageBox.question(
            self,
            "Letzte Warnung 🚨",
            f"Bist du dir wirklich WIRKLICH sicher, dass du Kunde {kundennr} löschen willst?\nDas kann man nicht rückgängig machen!",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if zweite_frage != QMessageBox.Yes:
            return  # abgebrochen

        # 3. Schritt: Jetzt wirklich löschen
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM KUNDE WHERE KUNDENNR = %s", (kundennr,))
        conn.commit()
        cursor.close()
        conn.close()
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

    def kunden_filtern(self):
        suchtext = self.suchfeld.text().lower()

        # Neuladen aller Kunden aus DB
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT KUNDENNR, NACHNAME, VORNAME, EMAIL, GEBURTSDATUM, STRASSE, HAUSNR, PLZ, ORT, TELEFON FROM KUNDE")
        daten = cursor.fetchall()
        cursor.close()
        conn.close()

        # Filter anwenden
        gefiltert = [
            row for row in daten
            if suchtext in str(row[1]).lower()
               or suchtext in str(row[2]).lower()
               or suchtext in str(row[3]).lower()
        ]

        self.table.setRowCount(len(gefiltert))
        self.table.setColumnCount(10)
        self.table.setHorizontalHeaderLabels([
            "Kundennr", "Nachname", "Vorname", "E-Mail", "Geburtsdatum",
            "Straße", "Hausnr.", "PLZ", "Ort", "Telefon"
        ])

        for i, row in enumerate(gefiltert):
            for j, value in enumerate(row):
                self.table.setItem(i, j, QTableWidgetItem(str(value)))


