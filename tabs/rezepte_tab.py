from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QHBoxLayout, QComboBox
from db import get_connection

class RezepteTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.setLayout(layout)

        #DropDown
        filter_layout = QHBoxLayout()
        self.allergen_filter = QComboBox()
        self.ern_filter = QComboBox()

        self.allergen_filter.addItem("Alle Allergene", None)
        self.ern_filter.addItem("Alle Ernährungsformen", None)

        self.allergen_filter.currentIndexChanged.connect(self.load_data)
        self.ern_filter.currentIndexChanged.connect(self.load_data)

        filter_layout.addWidget(self.allergen_filter)
        filter_layout.addWidget(self.ern_filter)
        layout.addLayout(filter_layout)

        #Tabelle
        self.table = QTableWidget()
        layout.addWidget(self.table)

        self.lade_filteroptionen()
        self.load_data()

    def lade_filteroptionen(self):
        connection = get_connection()
        cursor = connection.cursor()

        #Allergene laden
        cursor.execute("SELECT ALLERGEN_ID, ALLERGEN_NAME FROM ALLERGENE")
        for row in cursor.fetchall():
            self.allergen_filter.addItem(row["ALLERGEN_NAME"], row["ALLERGEN_ID"])

        #Ernährungsformen laden
        cursor.execute("SELECT KATEGORIE_ID, KATEGORIE_NAME FROM ERNAEHRUNGS_FORM")
        for row in cursor.fetchall():
            self.ern_filter.addItem(row["KATEGORIE_NAME"], row["KATEGORIE_ID"])

        cursor.close()
        connection.close()

    def load_data(self):
        allergen_id = self.allergen_filter.currentData()
        kategorie_id = self.ern_filter.currentData()

        connection = get_connection()
        cursor = connection.cursor()

        # SQL mit zwei optionalen Filtern (Allergen & Ernährungsform)
        query = """
        SELECT DISTINCT R.*
        FROM REZEPTE R
        LEFT JOIN REZEPT_ERNAEHRUNGSFORM RE ON R.REZEPT_ID = RE.REZEPT_ID
        LEFT JOIN REZEPT_ZUTATEN RZ ON R.REZEPT_ID = RZ.REZEPT_ID
        LEFT JOIN ZUTATEN_ALLERGENE ZA ON RZ.ZUTATEN_ID = ZA.ZUTATEN_ID
        WHERE (%s IS NULL OR RE.KATEGORIE_ID = %s)
          AND (%s IS NULL OR ZA.ALLERGEN_ID = %s)
        """

        cursor.execute(query, (kategorie_id, kategorie_id, allergen_id, allergen_id))
        data = cursor.fetchall()

        self.table.clear()
        self.table.setRowCount(len(data))
        if data:
            self.table.setColumnCount(len(data[0]))
            self.table.setHorizontalHeaderLabels(data[0].keys())
            for row_idx, row in enumerate(data):
                for col_idx, (key, value) in enumerate(row.items()):
                    self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))


        cursor.close()
        connection.close()
