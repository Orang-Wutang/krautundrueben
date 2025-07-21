from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QLineEdit, QPushButton, QHBoxLayout, QMessageBox, QComboBox, QDialog, QFormLayout
from db import get_connection
import os

class KundenTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.setLayout(layout)
        #DSVGO-Bericht herunterladen
        self.export_button = QPushButton("DSGVO-Bericht herunterladen")
        self.export_button.clicked.connect(self.export_ds_report)
        layout.addWidget(self.export_button)

        # Button-Leiste unterhalb der Tabelle
        button_layout = QHBoxLayout()
        button_layout.setSpacing(20)

        hinzu_button = QPushButton("Kunde hinzufügen")
        hinzu_button.clicked.connect(self.kunde_hinzufuegen)

        bearbeiten_button = QPushButton("Kunde bearbeiten")
        bearbeiten_button.clicked.connect(self.kunde_bearbeiten)

        loeschen_button = QPushButton("Kunde löschen")
        loeschen_button.clicked.connect(self.kunde_loeschen)

        button_layout.addStretch()
        button_layout.addWidget(hinzu_button)
        button_layout.addWidget(bearbeiten_button)
        button_layout.addWidget(loeschen_button)
        button_layout.addStretch()
        layout.addLayout(button_layout)

        #Suchfeld + Button
        such_layout = QHBoxLayout()
        self.suchfeld = QLineEdit()
        self.suchfeld.setPlaceholderText("Kundenname oder ID eingeben...")
        such_button = QPushButton("Suchen")
        such_button.clicked.connect(self.suche_kunden)

        such_layout.addWidget(self.suchfeld)
        such_layout.addWidget(such_button)
        layout.addLayout(such_layout)

        #Tabelle
        self.table = QTableWidget()
        layout.addWidget(self.table)

        self.load_data()

    def kunde_hinzufuegen(self):
        dialog = KundenDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.load_data()

    def kunde_bearbeiten(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Fehler", "Bitte wähle einen Kunden aus.")
            return

        daten = {}
        for i in range(self.table.columnCount()):
            header_item = self.table.horizontalHeaderItem(i)
            cell_item = self.table.item(row, i)
            if header_item and cell_item:
                daten[header_item.text()] = cell_item.text()

        dialog = KundenDialog(self, daten)
        if dialog.exec_() == QDialog.Accepted:
            self.load_data()

    def kunde_loeschen(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Fehler", "Bitte wähle einen Kunden aus.")
            return

        item = self.table.item(row, 0)
        if item is None:
            QMessageBox.warning(self, "Fehler", "Kunden-ID konnte nicht gelesen werden.")
            return

        kunden_id = item.text()

        bestaetigung = QMessageBox.question(
            self, "Löschen bestätigen",
            f"Möchtest du Kunde #{kunden_id} wirklich DSGVO-konform löschen? Dabei werden alle zugehörigen Daten entfernt.",
            QMessageBox.Yes | QMessageBox.No
        )

        if bestaetigung != QMessageBox.Yes:
            return

        connection = get_connection()
        cursor = connection.cursor()

        try:
            # 🔸 Schritt 1: Bestellungs-Zutaten löschen
            cursor.execute("""
                DELETE BZ FROM BESTELLUNG_ZUTATEN BZ
                JOIN BESTELLUNGEN B ON BZ.BESTELL_ID = B.BESTELL_ID
                WHERE B.KUNDEN_ID = %s
            """, (kunden_id,))

            # 🔸 Schritt 2: Bestellungen selbst löschen
            cursor.execute("DELETE FROM BESTELLUNGEN WHERE KUNDEN_ID = %s", (kunden_id,))

            # 🔸 Schritt 3: Kunde löschen
            cursor.execute("DELETE FROM KUNDEN WHERE KUNDEN_ID = %s", (kunden_id,))

            connection.commit()
            QMessageBox.information(self, "Erfolg", f"Kunde #{kunden_id} wurde vollständig gelöscht.")
            self.load_data()

        except Exception as e:
            connection.rollback()
            QMessageBox.critical(self, "Fehler", f"Fehler beim Löschen: {e}")

        finally:
            cursor.close()
            connection.close()

        self.load_data()
        QMessageBox.information(self, "Erfolg", f"Kunde #{kunden_id} wurde gelöscht.")

    def export_ds_report(self):
        from PyQt5.QtWidgets import QMessageBox
        import os

        selected_row = self.table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Fehler", "Bitte zuerst einen Kunden auswählen.")
            return

        kunden_id = int(self.table.item(selected_row, 0).text())  # erste Spalte: KUNDEN_ID

        connection = get_connection()
        cursor = connection.cursor()

        # Kundenstammdaten
        cursor.execute("SELECT * FROM KUNDEN WHERE KUNDEN_ID = %s", (kunden_id,))
        kunde = cursor.fetchone()

        # Bestellungen + Zutaten
        cursor.execute("""
                       SELECT B.BESTELL_DATUM, Z.ZUTATEN_BEZEICHNUNG, BZ.MENGE
                       FROM BESTELLUNGEN B
                                JOIN BESTELLUNG_ZUTATEN BZ ON B.BESTELL_ID = BZ.BESTELL_ID
                                JOIN ZUTATEN Z ON BZ.ZUTATEN_ID = Z.ZUTATEN_ID
                       WHERE B.KUNDEN_ID = %s
                       """, (kunden_id,))
        einkaeufe = cursor.fetchall()

        cursor.close()
        connection.close()

        # Bericht erstellen (als Textdatei)
        download_ordner = os.path.join(os.path.expanduser("~"), "Downloads")
        dateiname = os.path.join(download_ordner, f"DSGVO_Bericht_Kunde_{kunden_id}.txt")
        with open(dateiname, "w", encoding="utf-8") as f:
            f.write("DSGVO-Datenbericht\n")
            f.write("=" * 40 + "\n\n")
            f.write(f"Kunden_ID: {kunde['KUNDEN_ID']}\n")
            f.write(f"Name: {kunde['VORNAME']} {kunde['NACHNAME']}\n")
            f.write(f"Adresse: {kunde['STRASSE']} {kunde['HAUSNR']}, {kunde['PLZ']} {kunde['ORT']}\n")
            f.write(f"Telefon: {kunde['TELEFON']}\n")
            f.write(f"E-Mail: {kunde['EMAIL']}\n")
            f.write(f"Datenschutzerklärung akzeptiert: {kunde['DATENSCHUTZ_ERKL']}\n\n")

            f.write("Einkäufe:\n")
            for row in einkaeufe:
                f.write(
                    f"- {row['BESTELL_DATUM'].strftime('%Y-%m-%d %H:%M:%S')}: {row['ZUTATEN_BEZEICHNUNG']} ({row['MENGE']} g)\n")

        QMessageBox.information(self, "Fertig", f"Bericht wurde gespeichert unter:\n{os.path.abspath(dateiname)}")

    def load_data(self):
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM KUNDEN")
        data = cursor.fetchall()
        self.table.setRowCount(len(data))
        self.zeige_daten_in_tabelle(data)
        if data:
            self.table.setColumnCount(len(data[0]))
            self.table.setHorizontalHeaderLabels(data[0].keys())
            for row_idx, row in enumerate(data):
                for col_idx, (key, value) in enumerate(row.items()):
                    self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))
        cursor.close()
        connection.close()

    def suche_kunden(self):
        suchtext = self.suchfeld.text().strip()
        connection = get_connection()
        cursor = connection.cursor()

        if suchtext:
            query = """
                SELECT * FROM KUNDEN
                WHERE VORNAME LIKE %s OR NACHNAME LIKE %s OR CAST(KUNDEN_ID AS CHAR) LIKE %s
            """
            like_text = f"%{suchtext}%"
            cursor.execute(query, (like_text, like_text, like_text))
        else:
            cursor.execute("SELECT * FROM KUNDEN")

        data = cursor.fetchall()
        self.zeige_daten_in_tabelle(data)
        cursor.close()
        connection.close()

    def zeige_daten_in_tabelle(self, data):
        # Leere Inhalte, aber nicht ganze Tabelle
        self.table.clearContents()
        self.table.setRowCount(0)

        if not data:
            return

        self.table.setRowCount(len(data))
        self.table.setColumnCount(len(data[0]))
        self.table.setHorizontalHeaderLabels(data[0].keys())

        for row_idx, row in enumerate(data):
            for col_idx, (key, value) in enumerate(row.items()):
                self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))

class KundenDialog(QDialog):
    def __init__(self, parent=None, daten=None):
        super().__init__(parent)
        self.setWindowTitle("Kundendaten")
        self.setFixedSize(400, 400)

        layout = QFormLayout()
        self.vorname = QLineEdit()
        self.nachname = QLineEdit()
        self.strasse = QLineEdit()
        self.hausnr = QLineEdit()
        self.plz = QLineEdit()
        self.ort = QLineEdit()
        self.telefon = QLineEdit()
        self.email = QLineEdit()
        self.volljaehrig = QComboBox()
        self.volljaehrig.addItems(["J", "N"])
        self.datenschutz = QComboBox()
        self.datenschutz.addItems(["J", "N"])

        layout.addRow("Vorname:", self.vorname)
        layout.addRow("Nachname:", self.nachname)
        layout.addRow("Straße:", self.strasse)
        layout.addRow("Hausnummer:", self.hausnr)
        layout.addRow("PLZ:", self.plz)
        layout.addRow("Ort:", self.ort)
        layout.addRow("Telefon:", self.telefon)
        layout.addRow("E-Mail:", self.email)
        layout.addRow("Volljährig:", self.volljaehrig)
        layout.addRow("Datenschutzerklärung:", self.datenschutz)

        buttons = QHBoxLayout()
        speichern = QPushButton("Speichern")
        speichern.clicked.connect(self.speichern)
        abbrechen = QPushButton("Abbrechen")
        abbrechen.clicked.connect(self.reject)
        buttons.addWidget(speichern)
        buttons.addWidget(abbrechen)
        layout.addRow(buttons)

        self.setLayout(layout)
        self.kunden_id = None

        if daten:
            self.kunden_id = daten.get("KUNDEN_ID")
            self.vorname.setText(daten.get("VORNAME", ""))
            self.nachname.setText(daten.get("NACHNAME", ""))
            self.strasse.setText(daten.get("STRASSE", ""))
            self.hausnr.setText(daten.get("HAUSNR", ""))
            self.plz.setText(daten.get("PLZ", ""))
            self.ort.setText(daten.get("ORT", ""))
            self.telefon.setText(daten.get("TELEFON", ""))
            self.email.setText(daten.get("EMAIL", ""))
            self.volljaehrig.setCurrentText(daten.get("VOLLJAEHRIG", "J"))
            self.datenschutz.setCurrentText(daten.get("DATENSCHUTZ_ERKL", "J"))

    def speichern(self):
        daten = (
            self.vorname.text(), self.nachname.text(), self.strasse.text(),
            self.hausnr.text(), self.plz.text(), self.ort.text(),
            self.telefon.text(), self.email.text(),
            self.volljaehrig.currentText(), self.datenschutz.currentText()
        )

        connection = get_connection()
        cursor = connection.cursor()

        if self.kunden_id:
            query = """
                UPDATE KUNDEN SET VORNAME=%s, NACHNAME=%s, STRASSE=%s, HAUSNR=%s,
                PLZ=%s, ORT=%s, TELEFON=%s, EMAIL=%s, VOLLJAEHRIG=%s, DATENSCHUTZ_ERKL=%s
                WHERE KUNDEN_ID = %s
            """
            cursor.execute(query, daten + (self.kunden_id,))
        else:
            query = """
                INSERT INTO KUNDEN (VORNAME, NACHNAME, STRASSE, HAUSNR, PLZ, ORT,
                TELEFON, EMAIL, VOLLJAEHRIG, DATENSCHUTZ_ERKL)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, daten)

        connection.commit()
        cursor.close()
        connection.close()
        self.accept()
