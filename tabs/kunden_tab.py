from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QLineEdit, QPushButton, QHBoxLayout
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
            f.write(f"Kundennummer: {kunde['KUNDEN_ID']}\n")
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



