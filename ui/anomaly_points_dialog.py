from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QHBoxLayout, QHeaderView
)
from PyQt5.QtCore import pyqtSignal

# noinspection PyUnresolvedReferences
class AnomalyPointsDialog(QDialog):
    show_on_map_requested = pyqtSignal(list)

    def __init__(self, parent, points):
        super().__init__(parent)
        self.points = points
        self.parent_ref = parent
        self.setWindowTitle("Punkty anomalii")
        self.setMinimumSize(700, 450)

        layout = QVBoxLayout(self)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Indeks", "Lat", "Lon", "Głębokość [m]", "Typ"])
        self.table.setRowCount(len(points))
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)

        for row, p in enumerate(points):
            self.table.setItem(row, 0, QTableWidgetItem(str(p.get("index", ""))))
            self.table.setItem(row, 1, QTableWidgetItem(f"{p.get('lat', 0):.6f}"))
            self.table.setItem(row, 2, QTableWidgetItem(f"{p.get('lon', 0):.6f}"))
            depth = p.get('depth', 0)
            self.table.setItem(row, 3, QTableWidgetItem(f"{depth:.2f}"))
            self.table.setItem(row, 4, QTableWidgetItem(str(p.get("type", ""))))

        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)

        self.table.itemSelectionChanged.connect(self.on_selection_changed)

        btn_layout = QHBoxLayout()

        self.show_map_btn = QPushButton("Pokaż te punkty na mapie")
        self.show_map_btn.clicked.connect(self.on_show_map_clicked)

        self.close_btn = QPushButton("Zamknij")
        self.close_btn.clicked.connect(self.on_show_map_clicked)
        self.close_btn.clicked.connect(self.accept)

        btn_layout.addWidget(self.show_map_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(self.close_btn)

        layout.addLayout(btn_layout)

    def on_selection_changed(self):
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows: return
        row = selected_rows[0].row()
        try:
            point_index = int(self.table.item(row, 0).text())
            self.parent_ref.map_view.highlight_anomaly(self.points, point_index)
        except:
            pass

    def on_show_map_clicked(self):
        self.show_on_map_requested.emit(self.points)