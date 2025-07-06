import random
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QLineEdit, QPushButton, QDialog, QFormLayout,
    QDialogButtonBox, QMessageBox, QLabel, QHBoxLayout, QHeaderView
)

from db import get_connection

class KundenTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        # Suchfeld
        self.suchfeld = QLineEdit()
        self.suchfeld.setPlaceholderText("🔍 Kunden suchen nach Name, Vorname oder E-Mail")
        self.suchfeld.textChanged.connect(self.kunden_filtern)
        layout.addWidget(self.suchfeld)

        # Add-Button zentriert
        self.add_button = QPushButton("➕ Neuen Kunden anlegen")
        self.add_button.setFixedWidth(250)
        self.add_button.clicked.connect(self.kunde_hinzufuegen_dialog)

        button_layout_add = QHBoxLayout()
        button_layout_add.addStretch()
        button_layout_add.addWidget(self.add_button)
        button_layout_add.addStretch()
        layout.addLayout(button_layout_add)

        # Tabelle
        self.table = QTableWidget()
        layout.addWidget(self.table)

        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.table.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.table.horizontalHeader().setStretchLastSection(False)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)

        # Status-Label
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: green; font-style: italic; padding-left: 6px;")
        layout.addWidget(self.status_label)

        # Delete-Button zentriert
        self.delete_button = QPushButton("🗑️ Kunden löschen")
        self.delete_button.setFixedWidth(250)
        self.delete_button.clicked.connect(self.kunde_loeschen)

        button_layout_delete = QHBoxLayout()
        button_layout_delete.addStretch()
        button_layout_delete.addWidget(self.delete_button)
        button_layout_delete.addStretch()
        layout.addLayout(button_layout_delete)

        self.setLayout(layout)
        self.lade_kunden()

    def lade_kunden(self):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT KUNDENNR, VORNAME, NACHNAME, GEBURTSDATUM, STRASSE,
                   HAUSNR, PLZ, ORT, TELEFON, EMAIL
            FROM KUNDE
        """)
        daten = cursor.fetchall()
        cursor.close()
        conn.close()

        self.table.setRowCount(len(daten))
        self.table.setColumnCount(10)
        self.table.setHorizontalHeaderLabels([
            "Kundennr", "Vorname", "Nachname", "Geburtsdatum", "Straße",
            "Hausnr.", "PLZ", "Ort", "Telefon", "E-Mail"
        ])

        for i, row in enumerate(daten):
            for j, value in enumerate(row):
                self.table.setItem(i, j, QTableWidgetItem(str(value)))
            self.table.setRowHeight(i, 30)

        for i in range(self.table.columnCount()):
            self.table.setColumnWidth(i, 200)

    def kunden_filtern(self):
        suchtext = self.suchfeld.text().lower()

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT KUNDENNR, VORNAME, NACHNAME, GEBURTSDATUM, STRASSE,
                   HAUSNR, PLZ, ORT, TELEFON, EMAIL
            FROM KUNDE
        """)
        daten = cursor.fetchall()
        cursor.close()
        conn.close()

        gefiltert = [
            row for row in daten if
            suchtext in str(row[1]).lower() or
            suchtext in str(row[2]).lower() or
            suchtext in str(row[9]).lower()
        ]

        self.table.setRowCount(len(gefiltert))
        for i, row in enumerate(gefiltert):
            for j, value in enumerate(row):
                self.table.setItem(i, j, QTableWidgetItem(str(value)))
            self.table.setRowHeight(i, 30)

    def kunde_hinzufuegen_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Neuer Kunde")

        form = QFormLayout(dialog)
        felder = {}
        for label in ["Vorname", "Nachname", "E-Mail", "Geburtsdatum (JJJJ-MM-TT)",
                      "Straße", "Hausnummer", "PLZ", "Ort", "Telefon"]:
            felder[label] = QLineEdit()
            form.addRow(label + ":", felder[label])

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        form.addWidget(buttons)

        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)

        if dialog.exec_() == QDialog.Accepted:
            werte = {key: feld.text().strip() for key, feld in felder.items()}
            if not werte["Vorname"] or not werte["Nachname"] or not werte["E-Mail"]:
                self.zeige_statusmeldung("⚠️ Alle Pflichtfelder müssen ausgefüllt sein.")
                return

            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT MAX(KUNDENNR) FROM KUNDE")
            max_id = cursor.fetchone()[0] or 2000
            neue_id = max_id + 1
            cursor.execute("""
                INSERT INTO KUNDE (KUNDENNR, VORNAME, NACHNAME, EMAIL)
                VALUES (%s, %s, %s, %s)
            """, (neue_id, werte["Vorname"], werte["Nachname"], werte["E-Mail"]))
            conn.commit()
            cursor.close()
            conn.close()

            self.lade_kunden()
            self.zeige_statusmeldung("✅ Kunde erfolgreich gespeichert.")

    def kunde_loeschen(self):
        selected_items = self.table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Keine Auswahl", "Bitte wähle einen Kunden aus.")
            return

        zeile = selected_items[0].row()
        kundennr = self.table.item(zeile, 0).text()

        spruch = random.choice([
            "Willst du diesen Kunden wirklich löschen? 😢",
            "Vielleicht hatte er nur einen schlechten Tag 🤷‍",
            "Das ist dein letzter Moment, um es dir anders zu überlegen… 🤔",
            "Bist du bereit für diese Verantwortung?",
            f"Kundennummer {kundennr}… war's das wirklich wert?"
        ])

        if QMessageBox.question(self, "Letzte Chance 😬", spruch,
                                QMessageBox.Yes | QMessageBox.No) != QMessageBox.Yes:
            return

        if QMessageBox.question(self, "Letzte Warnung 🚨",
                                f"Sicher, dass du Kunde {kundennr} löschen willst?",
                                QMessageBox.Yes | QMessageBox.No) != QMessageBox.Yes:
            return

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM KUNDE WHERE KUNDENNR = %s", (kundennr,))
        conn.commit()
        cursor.close()
        conn.close()

        self.lade_kunden()
        self.zeige_statusmeldung("✅ Kunde erfolgreich gelöscht.")

    def zeige_statusmeldung(self, text: str, dauer_ms: int = 3000):
        self.status_label.setText(text)
        QTimer.singleShot(dauer_ms, lambda: self.status_label.setText(""))
