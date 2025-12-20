from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QTableWidget,
    QTableWidgetItem, QPushButton
)


class AnomalyPointsDialog(QDialog):
    def __init__(self, parent, points):
        super().__init__(parent)
        self.points = points
        self.parent_ref = parent  # Zachowujemy referencję do MainWindow
        self.setWindowTitle("Punkty anomalii")
        self.setMinimumSize(400, 300)

        layout = QVBoxLayout(self)

        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Indeks", "Latitude", "Longitude"])
        self.table.setRowCount(len(points))
        self.table.setSelectionBehavior(QTableWidget.SelectRows)  # Całe wiersze
        self.table.setSelectionMode(QTableWidget.SingleSelection)  # Tylko jeden na raz

        for row, p in enumerate(points):
            self.table.setItem(row, 0, QTableWidgetItem(str(p["index"])))
            self.table.setItem(row, 1, QTableWidgetItem(f"{p['lat']:.6f}"))
            self.table.setItem(row, 2, QTableWidgetItem(f"{p['lon']:.6f}"))

        # Łączymy kliknięcie w tabeli z funkcją podświetlania
        self.table.itemSelectionChanged.connect(self.on_selection_changed)

        self.table.resizeColumnsToContents()
        layout.addWidget(self.table)

        close_btn = QPushButton("Zamknij")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)

    def on_selection_changed(self):
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            return

        row = selected_rows[0].row()
        # Pobieramy ID z pierwszej kolumny (index)
        try:
            point_index = int(self.table.item(row, 0).text())
            # Wywołujemy funkcję w map_view przez MainWindow
            self.parent_ref.map_view.highlight_anomaly(self.points, point_index)
        except (ValueError, AttributeError):
            pass