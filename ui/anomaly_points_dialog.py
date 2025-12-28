from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QHBoxLayout, QHeaderView, QLabel, QFileDialog
)
from PyQt5.QtCore import pyqtSignal
from ui.export_dialog import ExportOptionsDialog
from logic.exporter import export_to_geojson

# noinspection PyUnresolvedReferences
class AnomalyPointsDialog(QDialog):
    show_on_map_requested = pyqtSignal(list)

    def __init__(self, parent, points):
        super().__init__(parent)
        self.points = points
        self.parent_ref = parent
        self.selected_chain = []
        self.is_linking_mode = False

        self.setWindowTitle("Punkty anomalii")
        self.setMinimumSize(600, 400)

        layout = QVBoxLayout(self)

        self.mode_label = QLabel("Tryb przeglądania")
        layout.addWidget(self.mode_label)

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

        self.start_link_btn = QPushButton("Połącz anomalie")
        self.start_link_btn.clicked.connect(self.enter_linking_mode)

        self.add_to_chain_btn = QPushButton("Zaznacz kolejny punkt")
        self.add_to_chain_btn.clicked.connect(self.add_current_to_chain)
        self.add_to_chain_btn.setEnabled(False)

        self.finish_link_btn = QPushButton("Zakończ łączenie")
        self.finish_link_btn.clicked.connect(self.finish_linking)
        self.finish_link_btn.setEnabled(False)

        self.export_btn = QPushButton("Eksportuj GIS")
        self.export_btn.clicked.connect(self.handle_export)
        self.export_btn.setEnabled(len(getattr(self.parent_ref, 'all_connections', [])) > 0)

        self.show_map_btn = QPushButton("Pokaż na mapie")
        self.show_map_btn.clicked.connect(self.on_show_map_clicked)

        self.close_btn = QPushButton("Zamknij")
        self.close_btn.clicked.connect(self.accept)

        btn_layout.addWidget(self.start_link_btn)
        btn_layout.addWidget(self.add_to_chain_btn)
        btn_layout.addWidget(self.finish_link_btn)
        btn_layout.addWidget(self.export_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(self.show_map_btn)
        btn_layout.addWidget(self.close_btn)

        layout.addLayout(btn_layout)

    def on_selection_changed(self):
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            self.add_to_chain_btn.setEnabled(False)
            return

        self.add_to_chain_btn.setEnabled(self.is_linking_mode)

        row = selected_rows[0].row()
        try:
            point_index = int(self.table.item(row, 0).text())
            self.parent_ref.map_view.highlight_anomaly(self.points, point_index)
        except:
            pass

    def enter_linking_mode(self):
        self.is_linking_mode = True
        self.selected_chain = []
        self.start_link_btn.setEnabled(False)
        self.finish_link_btn.setEnabled(True)
        self.update_linking_status()

    def update_linking_status(self):
        count = len(self.selected_chain)
        self.mode_label.setText(f"TRYB ŁĄCZENIA: Wybierz punkt nr {count + 1} i kliknij 'Zaznacz kolejny'")
        self.mode_label.setStyleSheet("font-weight: bold; color: red;")

    def add_current_to_chain(self):
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows: return

        row = selected_rows[0].row()
        p_idx = int(self.table.item(row, 0).text())
        point_data = next((p for p in self.points if p['index'] == p_idx), None)

        if point_data:
            self.selected_chain.append(point_data)
            self.update_linking_status()

    def finish_linking(self):
        if len(self.selected_chain) >= 2:
            self.parent_ref.map_view.draw_anomaly_connection(self.selected_chain)
            if not hasattr(self.parent_ref, 'all_connections'):
                self.parent_ref.all_connections = []
            self.parent_ref.all_connections.append(self.selected_chain)
            self.parent_ref.statusBar().showMessage(
                f"Narysowano połączenie między {len(self.selected_chain)} anomaliami.")
            self.export_btn.setEnabled(True)

        self.is_linking_mode = False
        self.start_link_btn.setEnabled(True)
        self.add_to_chain_btn.setEnabled(False)
        self.finish_link_btn.setEnabled(False)
        self.mode_label.setText("Tryb: Przeglądanie punktów")
        self.mode_label.setStyleSheet("")
        self.selected_chain = []

    def handle_export(self):
        exp_dialog = ExportOptionsDialog(self)
        if exp_dialog.exec_() == QDialog.Accepted:
            options = exp_dialog.get_options()
            file_path, _ = QFileDialog.getSaveFileName(self, "Zapisz dane GIS", "", "GeoJSON (*.geojson)")
            if file_path:
                try:
                    export_to_geojson(
                        file_path,
                        export_points=options['points'],
                        export_profiles=options['profiles'],
                        export_links=options['links'],
                        points_data=self.points,
                        profiles_data=self.parent_ref.map_view.profile_history,
                        links_data=getattr(self.parent_ref, 'all_connections', [])
                    )
                    self.parent_ref.statusBar().showMessage(f"Wyeksportowano pomyślnie do {file_path}")
                except Exception as e:
                    self.parent_ref.statusBar().showMessage(f"Błąd eksportu: {e}")

    def on_show_map_clicked(self):
        self.show_on_map_requested.emit(self.points)