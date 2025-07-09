# tabs/zutaten_tab.py
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QLineEdit, QMessageBox, QComboBox, QHBoxLayout, QPushButton, QHeaderView

from db import get_sql_connection


class ZutatenTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        self.setStyleSheet("""
            QToolTip {
                background-color: white;
                color: black;
                border: 1px solid gray;
                padding: 5px;
                font-size: 11pt;
            }
        """)

        self.suchfeld: QLineEdit = QLineEdit()
        self.suchfeld.setPlaceholderText("🔍 Zutaten suchen nach Bezeichnung oder Einheit")
        self.suchfeld.textChanged.connect(self.zutaten_filtern)
        layout.addWidget(self.suchfeld)

        self.table: QTableWidget = QTableWidget()
        layout.addWidget(self.table)
        self.setLayout(layout)

        # Erst die ComboBoxen erzeugen
        self.combo_allergen = QComboBox()
        self.combo_ernaehrung = QComboBox()

        self.combo_allergen.setToolTip("🚫 Zutaten ohne dieses Allergen")
        self.combo_ernaehrung.setToolTip("🧘 Zutaten aus Rezepten mit dieser Kategorie")

        # Dann ins Layout einbauen (optional nebeneinander)
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(self.combo_allergen)
        filter_layout.addWidget(self.combo_ernaehrung)
        layout.addLayout(filter_layout)

        # Jetzt DB-Verbindung und Inhalte einfüllen
        conn = get_sql_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT ALLERGENNR, BEZEICHNUNG FROM ALLERGEN")
        self.combo_allergen.addItem("Alle", -1)
        for allergen_id, bezeichnung in cursor.fetchall():
            self.combo_allergen.addItem(bezeichnung, allergen_id)

        cursor.execute("SELECT KATEGORIENR, BEZEICHNUNG FROM ERNAEHRUNGSKATEGORIE")
        self.combo_ernaehrung.addItem("Alle", -1)
        for kat_id, bezeichnung in cursor.fetchall():
            self.combo_ernaehrung.addItem(bezeichnung, kat_id)

        cursor.close()
        conn.close()

        self.filter_button = QPushButton("🔎 Filter anwenden")
        self.filter_button.setFixedWidth(250)
        self.filter_button.clicked.connect(self.zutaten_filtern)

        button_layout_filter = QHBoxLayout()
        button_layout_filter.addStretch()
        button_layout_filter.addWidget(self.filter_button)
        button_layout_filter.addStretch()
        layout.addLayout(button_layout_filter)

        self.table.itemChanged.connect(self.bestand_aktualisieren)

    def zutaten_filtern(self):
        self.table.clearContents()

        suchtext = self.suchfeld.text().lower()
        allergen_id = self.combo_allergen.currentData()
        kat_id = self.combo_ernaehrung.currentData()

        sql = """
              SELECT DISTINCT z.ZUTATENNR, z.BEZEICHNUNG, z.BESTAND, z.EINHEIT, z.NETTOPREIS
              FROM ZUTAT z
                       LEFT JOIN REZEPTZUTAT rz ON z.ZUTATENNR = rz.ZUTATENNR
                       LEFT JOIN REZEPTERNAEHRUNG re ON rz.REZEPTNR = re.REZEPTNR
              WHERE 1 = 1 \
              """
        params = []

        if suchtext:
            sql += " AND (LOWER(z.BEZEICHNUNG) LIKE %s OR LOWER(z.EINHEIT) LIKE %s)"
            like = f"%{suchtext}%"
            params.extend([like, like])

        if allergen_id is not None and allergen_id != -1:
            sql += """
                    AND NOT EXISTS (
                        SELECT 1 FROM ZUTATALLERGEN za
                        WHERE za.ZUTATENNR = z.ZUTATENNR AND za.ALLERGENNR = %s
                    )
                """
            params.append(allergen_id)

        if kat_id != -1:
            sql += " AND re.KATEGORIENR = %s"
            params.append(kat_id)

        conn = get_sql_connection()
        cursor = conn.cursor()
        cursor.execute(sql, params)
        zutaten = cursor.fetchall()

        if not zutaten:
            QMessageBox.information(self, "Keine Ergebnisse", "Es wurden keine passenden Zutaten gefunden.")
            self.table.setRowCount(0)
            return

        self.table.setRowCount(len(zutaten))
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(
            ["Bezeichnung", "Bestand", "Einheit", "Nettopreis", "Allergene", "Kategorien"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

        for zeile, (zutnr, bez, bestand, einheit, preis) in enumerate(zutaten):
            # Allergene abfragen
            cursor.execute("""
                           SELECT a.BEZEICHNUNG
                           FROM ZUTATALLERGEN za
                                    JOIN ALLERGEN a ON za.ALLERGENNR = a.ALLERGENNR
                           WHERE za.ZUTATENNR = %s
                           """, (zutnr,))
            allergene = ", ".join([a[0] for a in cursor.fetchall()]) or "—"

            # Kategorien abfragen
            cursor.execute("""
                           SELECT DISTINCT k.BEZEICHNUNG
                           FROM REZEPTZUTAT rz
                                    JOIN REZEPTERNAEHRUNG re ON rz.REZEPTNR = re.REZEPTNR
                                    JOIN ERNAEHRUNGSKATEGORIE k ON re.KATEGORIENR = k.KATEGORIENR
                           WHERE rz.ZUTATENNR = %s
                           """, (zutnr,))
            kategorien = ", ".join([k[0] for k in cursor.fetchall()]) or "—"

            self.table.setItem(zeile, 0, QTableWidgetItem(bez))
            self.table.setItem(zeile, 1, QTableWidgetItem(str(bestand)))
            self.table.setItem(zeile, 2, QTableWidgetItem(einheit))
            self.table.setItem(zeile, 3, QTableWidgetItem(f"{preis:.2f}"))
            self.table.setItem(zeile, 4, QTableWidgetItem(allergene))
            self.table.setItem(zeile, 5, QTableWidgetItem(kategorien))

        cursor.close()
        conn.close()

    def bestand_aktualisieren(self, item):
        spalte = item.column()
        if spalte != 1:  # Nur "Bestand"-Spalte (Index 1) darf geändert werden
            return

        zeile = item.row()
        bezeichnung = self.table.item(zeile, 0).text()
        neuer_bestand = item.text()

        # Prüfen ob Zahl
        try:
            neuer_bestand = float(neuer_bestand)
        except ValueError:
            QMessageBox.warning(self, "Ungültiger Wert", "Bitte gib eine gültige Zahl für den Bestand ein.")
            return

        conn = get_sql_connection()
        cursor = conn.cursor()
        cursor.execute("""
                       UPDATE ZUTAT
                       SET BESTAND = %s
                       WHERE BEZEICHNUNG = %s
                       """, (neuer_bestand, bezeichnung))
        conn.commit()
        cursor.close()
        conn.close()
