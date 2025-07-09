import random
import datetime
from tabs.db import get_sql_connection, get_mongo_connection, get_mongo_collection
from PyQt5.QtCore import Qt, QTimer, QTime
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QLineEdit, QPushButton, QDialog, QFormLayout,
    QDialogButtonBox, QMessageBox, QLabel, QHBoxLayout, QHeaderView
)

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
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.table.cellDoubleClicked.connect(self.kunde_bearbeiten_dialog)

        layout.addWidget(self.table)

        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.table.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.table.horizontalHeader().setStretchLastSection(False)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

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
        mongo_db = get_mongo_connection()
        feedbacks_collection = mongo_db["feedbacks"]
        conn = get_sql_connection()
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
        self.table.setColumnCount(11)
        self.table.setHorizontalHeaderLabels([
            "Kundennr", "Vorname", "Nachname", "Geburtsdatum", "Straße",
            "Hausnr.", "PLZ", "Ort", "Telefon", "E-Mail", "Feedbacks"
        ])

        for i, row in enumerate(daten):
            for j, value in enumerate(row):
                self.table.setItem(i, j, QTableWidgetItem(str(value)))

            # Feedback-Spalte (Index 10) befüllen
            kundennr = row[0]
            anzahl_feedbacks = feedbacks_collection.count_documents({"kunde_id": kundennr})
            feedback_item = QTableWidgetItem(f"{anzahl_feedbacks} Feedback(s)")
            feedback_item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)  # Nicht editierbar
            self.table.setItem(i, 10, feedback_item)

            self.table.setRowHeight(i, 30)

        for i in range(self.table.columnCount()):
            self.table.setColumnWidth(i, 200)

    def kunden_filtern(self):
        suchtext = self.suchfeld.text().lower()

        conn = get_sql_connection()
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

            conn = get_sql_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT MAX(KUNDENNR) FROM KUNDE")
            max_id = cursor.fetchone()[0] or 2000
            neue_id = max_id + 1
            cursor.execute("""
                           INSERT INTO KUNDE (KUNDENNR, VORNAME, NACHNAME, EMAIL, GEBURTSDATUM, STRASSE, HAUSNR, PLZ,
                                              ORT, TELEFON)
                           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                           """, (
                               neue_id,
                               werte["Vorname"],
                               werte["Nachname"],
                               werte["E-Mail"],
                               werte["Geburtsdatum (JJJJ-MM-TT)"] or None,
                               werte["Straße"] or None,
                               werte["Hausnummer"] or None,
                               werte["PLZ"] or None,
                               werte["Ort"] or None,
                               werte["Telefon"] or None
                           ))
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

        conn = get_sql_connection()
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

    def kunde_bearbeiten_dialog(self, row, column):
        aktuelle_bezeichnung = self.table.horizontalHeaderItem(column).text()
        item = self.table.item(row, column)
        if item is None:
            QMessageBox.warning(self, "Fehler", "Dieses Feld ist leer und kann nicht bearbeitet werden.")
            return

        alter_wert = item.text()
        kundennr = int(self.table.item(row, 0).text())  # Spalte 0 = KUNDENNR

        # Wenn auf Spalte "Feedbacks" (Spalte 10) geklickt wurde
        if column == 10:
            mongo_db = get_mongo_connection()
            feedback_collection = mongo_db["feedbacks"]
            feedbacks = feedback_collection.find({"kunde_id": kundennr})

            texte = "\n\n".join([
                f"{f.get('datum', '??')}: {f.get('text', '')}" for f in feedbacks
            ])

            if not texte:
                texte = "Keine Feedbacks vorhanden."

            QMessageBox.information(self, f"Feedbacks von Kunde {kundennr}", texte)

            # Frage, ob neues Feedback eingetragen werden soll
            if QMessageBox.question(self, "Neues Feedback hinzufügen?",
                                    "Möchtest du ein Feedback zu diesem Kunden hinzufügen?",
                                    QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
                self.feedback_hinzufuegen_dialog(kundennr)

            return  # Damit der normale Bearbeiten-Dialog nicht mehr geöffnet wird

        dialog = QDialog(self)
        dialog.setWindowTitle(f"{aktuelle_bezeichnung} bearbeiten")

        layout = QVBoxLayout(dialog)

        feld = QLineEdit()
        feld.setText(alter_wert)
        layout.addWidget(QLabel(f"Neuer Wert für {aktuelle_bezeichnung}:"))
        layout.addWidget(feld)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        layout.addWidget(buttons)

        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)


        if dialog.exec_() == QDialog.Accepted:
            neuer_wert = feld.text().strip()

            # Mapping Spalte zu DB-Spaltennamen
            spalten_map = {
                "Vorname": "VORNAME",
                "Nachname": "NACHNAME",
                "Geburtsdatum": "GEBURTSDATUM",
                "Straße": "STRASSE",
                "Hausnr.": "HAUSNR",
                "PLZ": "PLZ",
                "Ort": "ORT",
                "Telefon": "TELEFON",
                "E-Mail": "EMAIL"
            }

            spaltenname = spalten_map.get(aktuelle_bezeichnung)

            if not spaltenname:
                QMessageBox.warning(self, "Nicht editierbar", "Diese Spalte kann nicht bearbeitet werden.")
                return

            # In DB aktualisieren
            conn = get_sql_connection()
            cursor = conn.cursor()
            cursor.execute(
                f"UPDATE KUNDE SET {spaltenname} = %s WHERE KUNDENNR = %s",
                (neuer_wert, kundennr)
            )
            conn.commit()
            cursor.close()
            conn.close()

            try:
                collection = get_mongo_collection()
                collection.insert_one({
                    "aktion": "Kundendaten bearbeitet",
                    "kundennr": kundennr,
                    "feld": spaltenname,
                    "neuer_wert": neuer_wert,
                    "zeitpunkt": datetime.datetime.now().isoformat()
                })
            except Exception as e:
                print(f"⚠️ Fehler beim Speichern in MongoDB: {e}")

            # Tabelle neu laden
            self.lade_kunden()
            self.zeige_statusmeldung("✅ Kundendaten aktualisiert.")

    def feedback_hinzufuegen_dialog(self, kundennr):
        dialog = QDialog(self)
        dialog.setWindowTitle(f"📝 Feedback zu Kunde {kundennr}")
        layout = QVBoxLayout(dialog)

        feld = QLineEdit()
        feld.setPlaceholderText("Feedback eingeben...")
        layout.addWidget(QLabel("Neues Feedback:"))
        layout.addWidget(feld)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        layout.addWidget(buttons)

        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)

        if dialog.exec_() == QDialog.Accepted:
            feedback_text = feld.text().strip()
            if feedback_text:
                mongo_db = get_mongo_connection()
                feedbacks = mongo_db["feedbacks"]
                feedbacks.insert_one({
                    "kunde_id": kundennr,
                    "datum": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "text": feedback_text
                })
                self.zeige_statusmeldung("✅ Feedback gespeichert.")
            else:
                self.zeige_statusmeldung("⚠️ Feedback darf nicht leer sein.")

    def feedback_hinzufuegen_dialog(self, kundennr):

        dialog = QDialog(self)
        dialog.setWindowTitle(f"📝 Feedback zu Kunde {kundennr}")
        layout = QVBoxLayout(dialog)

        textfeld = QLineEdit()
        textfeld.setPlaceholderText("Feedback eingeben...")
        layout.addWidget(textfeld)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        layout.addWidget(buttons)

        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)

        if dialog.exec_() == QDialog.Accepted:
            feedback_text = textfeld.text().strip()
            if feedback_text:
                mongo_db = get_mongo_connection()
                feedbacks = mongo_db["feedbacks"]
                feedbacks.insert_one({
                    "kunde_id": kundennr,
                    "datum": datetime.datetime.now().strftime("%H:%M:%S"),
                    "text": feedback_text
                })
                self.zeige_statusmeldung("✅ Feedback gespeichert.")
                self.lade_kunden()
            else:
                self.zeige_statusmeldung("⚠️ Feedback darf nicht leer sein.")



