from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QCheckBox,
    QPushButton, QFileDialog, QHBoxLayout, QLineEdit
)
import pandas as pd
from folium import folium


class CsvImportDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Import pliku CSV")
        self.setMinimumWidth(400)

        self.file_path = ""

        layout = QVBoxLayout(self)

        file_layout = QHBoxLayout()
        self.file_edit = QLineEdit()
        self.file_edit.setReadOnly(True)
        browse_btn = QPushButton("Wybierz plik...")
        browse_btn.clicked.connect(self.browse_file)

        file_layout.addWidget(self.file_edit)
        file_layout.addWidget(browse_btn)

        layout.addLayout(file_layout)

        self.header_checkbox = QCheckBox("Plik zawiera nagłówki w pierwszym wierszu")
        self.header_checkbox.setChecked(True)
        layout.addWidget(self.header_checkbox)

        info_label = QLabel(
            "Założenie: kolumna 2 = x, kolumna 'amplituda' = oś Y.\n"
            "Ułożenie kolumn jest zawsze takie samo."
        )
        layout.addWidget(info_label)

        btn_layout = QHBoxLayout()

        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(self.accept)
        btn_layout.addWidget(ok_btn)

        cancel_btn = QPushButton("Anuluj")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        layout.addLayout(btn_layout)

    def browse_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Wybierz plik CSV",
            "",
            "Pliki CSV (*.csv);;Wszystkie pliki (*.*)"
        )
        if path:
            self.file_path = path
            self.file_edit.setText(path)

def open_csv_import_dialog(parent, plot_view, delta, delta_reference=0):
    dialog = CsvImportDialog(parent)
    if dialog.exec_() != QDialog.Accepted:
        return

    if not dialog.file_path:
        parent.statusBar().showMessage("Nie wybrano pliku CSV")
        return

    has_header = dialog.header_checkbox.isChecked()
    sep = ";"

    try:
        if has_header:
            df = pd.read_csv(dialog.file_path, sep=sep, decimal=',')
        else:
            df = pd.read_csv(dialog.file_path, sep=sep, header=None, decimal=',')
    except Exception as e:
        parent.statusBar().showMessage(f"Błąd podczas wczytywania pliku: {e}")
        return

    if df.shape[1] < 3:
        parent.statusBar().showMessage(
            f"Za mało kolumn w pliku (znaleziono {df.shape[1]}). Oczekiwane minimum: 3."
        )
        return

    x_raw = pd.to_numeric(df.iloc[:, 1], errors='coerce').values
    x_distance = x_raw - x_raw[0]

    if has_header and "amplituda" in df.columns:
        y = pd.to_numeric(df["amplituda"], errors='coerce').values
    else:
        y = pd.to_numeric(df.iloc[:, 2], errors='coerce').values

    plot_view.set_data(x_distance, y)

    start_lat = getattr(parent, "profile_start_x", None)
    start_lon = getattr(parent, "profile_start_y", None)
    azimuth = getattr(parent, "profile_azimuth", 90.0)

    current_profile_deltas = getattr(parent, "profile_deltas", [])
    total_delta = 0.0

    if delta == 0:
        parent.map_view.map_obj = folium.Map(location=[start_lat, start_lon], zoom_start=19)
        parent.profile_deltas = [0]
        total_delta = 0
    else:

        if delta_reference == 0:
            total_delta = sum(current_profile_deltas) + delta
            parent.profile_deltas.append(delta)

        elif delta_reference == 1:
            total_delta = delta
            parent.profile_deltas = [total_delta]

    parent.map_view.draw_profile(x_distance, start_lat, start_lon, azimuth, total_delta)