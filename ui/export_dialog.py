from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QCheckBox, QHBoxLayout, QPushButton


class ExportOptionsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Eksport do QGIS (GeoJSON)")
        self.setFixedWidth(300)

        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("<b>Wybierz elementy do eksportu:</b>"))

        self.cb_points = QCheckBox("Anomalie (Punkty)")
        self.cb_points.setChecked(True)
        layout.addWidget(self.cb_points)

        self.cb_profiles = QCheckBox("Profile (Linie bazowe)")
        self.cb_profiles.setChecked(True)
        layout.addWidget(self.cb_profiles)

        self.cb_links = QCheckBox("Połączenia anomalii (Linie)")
        self.cb_links.setChecked(True)
        layout.addWidget(self.cb_links)

        btn_layout = QHBoxLayout()
        self.btn_export = QPushButton("Eksportuj")
        self.btn_export.clicked.connect(self.accept)

        self.btn_cancel = QPushButton("Anuluj")
        self.btn_cancel.clicked.connect(self.reject)

        btn_layout.addWidget(self.btn_export)
        btn_layout.addWidget(self.btn_cancel)

        layout.addLayout(btn_layout)

    def get_options(self):
        return {
            "points": self.cb_points.isChecked(),
            "profiles": self.cb_profiles.isChecked(),
            "links": self.cb_links.isChecked()
        }