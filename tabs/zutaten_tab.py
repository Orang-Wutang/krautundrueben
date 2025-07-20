from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QHBoxLayout, QComboBox
from db import get_connection

class ZutatenTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Filterbereich
        filter_layout = QHBoxLayout()
        self.allergen_filter = QComboBox()
        self.allergen_filter.addItem("Alle Allergene", None)
        self.allergen_filter.currentIndexChanged.connect(self.load_data)
        filter_layout.addWidget(self.allergen_filter)
        layout.addLayout(filter_layout)

        #Tabelle
        self.table = QTableWidget()
        layout.addWidget(self.table)

        self.lade_filteroptionen()
        self.load_data()

    def lade_filteroptionen(self):
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT ALLERGEN_ID, ALLERGEN_NAME FROM ALLERGENE")
        for row in cursor.fetchall():
            self.allergen_filter.addItem(row["ALLERGEN_NAME"], row["ALLERGEN_ID"])
        cursor.close()
        connection.close()


    def load_data(self):
        allergen_id = self.allergen_filter.currentData()
        connection = get_connection()
        cursor = connection.cursor()

        if allergen_id is not None:
            query = """
                SELECT DISTINCT Z.*
                FROM ZUTATEN Z
                JOIN ZUTATEN_ALLERGENE ZA ON Z.ZUTATEN_ID = ZA.ZUTATEN_ID
                WHERE ZA.ALLERGEN_ID = %s
            """
            cursor.execute(query, (allergen_id,))
        else:
            query = "SELECT * FROM ZUTATEN"
            cursor.execute(query)

        data = cursor.fetchall()
        self.table.setRowCount(len(data))
        if data:
            self.table.setColumnCount(len(data[0]))
            self.table.setHorizontalHeaderLabels(data[0].keys())
            for row_idx, row in enumerate(data):
                for col_idx, (key, value) in enumerate(row.items()):
                    self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))

        cursor.close()
        connection.close()
