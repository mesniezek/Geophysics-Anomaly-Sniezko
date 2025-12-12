from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QCheckBox,
    QPushButton, QFileDialog, QHBoxLayout, QLineEdit, QComboBox
)
import pandas as pd
from folium import folium
import io
import re

# noinspection PyUnresolvedReferences
class ProfileImportDialog(QDialog):
    def __init__(self, parent=None, is_dat=False):
        super().__init__(parent)
        self.setWindowTitle("Import danych profilu")
        self.setMinimumWidth(400)
        self.setMinimumHeight(400)

        self.file_path = ""
        self.x_column_index = 0
        self.y_column_index = 1
        self.is_dat = is_dat

        layout = QVBoxLayout(self)

        file_layout = QHBoxLayout()
        self.file_edit = QLineEdit()
        self.file_edit.setReadOnly(True)

        browse_btn = QPushButton("Wybierz plik...")
        browse_btn.clicked.connect(self.browse_file)

        file_layout.addWidget(self.file_edit)
        file_layout.addWidget(browse_btn)

        layout.addLayout(file_layout)

        sep_label = QLabel("Wybierz Separator:")
        layout.addWidget(sep_label)
        self.separator_box = QComboBox()
        self.separator_box.addItems([
            "Średnik (;)",
            "Przecinek (,)",
            "Spacja/Tab (DAT/Txt)"
        ])

        if self.is_dat:
            self.separator_box.setCurrentIndex(2)
        else:
            self.separator_box.setCurrentIndex(0)

        layout.addWidget(self.separator_box)

        self.header_checkbox = QCheckBox("Plik zawiera nagłówki w pierwszym wierszu")
        self.header_checkbox.setChecked(not self.is_dat)
        layout.addWidget(self.header_checkbox)

        x_col_label = QLabel("Indeks kolumny dla osi X (Odległość):")
        layout.addWidget(x_col_label)
        self.x_column_edit = QLineEdit()
        self.x_column_edit.setPlaceholderText("Wpisz indeks kolumny X (np. 0)")
        self.x_column_edit.setText(str(self.x_column_index))
        layout.addWidget(self.x_column_edit)

        y_col_label = QLabel("Indeks kolumny dla osi Y (Wartość):")
        layout.addWidget(y_col_label)
        self.y_column_edit = QLineEdit()
        self.y_column_edit.setPlaceholderText("Wpisz indeks kolumny Y (np. 1)")
        self.y_column_edit.setText(str(self.y_column_index))
        layout.addWidget(self.y_column_edit)

        info_index = QLabel(
            "Indeks 0 to kolumna A, 1 to kolumna B itd.\n"
            "Wartości dziesiętne: Przecinek (,) (domyślnie)."
        )
        layout.addWidget(info_index)

        btn_layout = QHBoxLayout()
        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(self.accept)
        btn_layout.addWidget(ok_btn)

        cancel_btn = QPushButton("Anuluj")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        layout.addLayout(btn_layout)

    def browse_file(self):
        filter_str = "Pliki danych (*.csv *.dat);;Wszystkie pliki (*.*)"
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Wybierz plik danych profilu",
            "",
            filter_str
        )
        if path:
            self.file_path = path
            self.file_edit.setText(path)

    def get_x_column_index(self):
        try:
            return int(self.x_column_edit.text())
        except ValueError:
            return 0

    def get_y_column_index(self):
        try:
            return int(self.y_column_edit.text())
        except ValueError:
            return 1

    def get_separator(self):
        index = self.separator_box.currentIndex()
        if index == 0:
            return ";"
        elif index == 1:
            return ","
        elif index == 2:
            return r'\s+'
        return ";"


def import_profile_data(parent, plot_view, delta, delta_reference=0, file_type_selection="Plik .csv"):
    is_dat = file_type_selection == "Plik .dat"
    dialog = ProfileImportDialog(parent, is_dat=is_dat)
    if dialog.exec_() != QDialog.Accepted:
        return

    if not dialog.file_path:
        parent.statusBar().showMessage("Nie wybrano pliku danych")
        return

    has_header = dialog.header_checkbox.isChecked()
    x_col_index = dialog.get_x_column_index()
    y_col_index = dialog.get_y_column_index()
    sep = dialog.get_separator()

    if x_col_index == y_col_index:
        parent.statusBar().showMessage(f"Błąd: Indeksy kolumn X ({x_col_index}) i Y ({y_col_index}) muszą być różne.")
        return

    try:
        if sep == r'\s+' and has_header:
            with open(dialog.file_path, 'r', encoding='utf-8') as f:
                content = f.readlines()
                header_line = content[0].strip()
                data_content = "".join(content[1:])

            header_line = re.sub(r'["\t\s,;]', ' ', header_line).strip()
            header_names = [name for name in header_line.split() if name]

            df = pd.read_csv(
                io.StringIO(data_content),
                sep=sep,
                header=None,
                decimal=',',
                engine='python'
            )

            if not df.empty and df.iloc[:, 0].isnull().all():
                df = df.iloc[:, 1:].reset_index(drop=True)

            if df.shape[1] == len(header_names):
                df.columns = header_names
                has_header = True
            else:
                has_header = False
        else:
            if sep == r'\s+':
                df = pd.read_csv(
                    dialog.file_path,
                    sep=sep,
                    header=(0 if has_header else None),
                    decimal=',',
                    engine='python'
                )
                if not df.empty and df.iloc[:, 0].isnull().all():
                    df = df.iloc[:, 1:].reset_index(drop=True)
            else:
                df = pd.read_csv(
                    dialog.file_path,
                    sep=sep,
                    header=(0 if has_header else None),
                    decimal=','
                )

    except Exception as e:
        parent.statusBar().showMessage(f"Błąd podczas wczytywania pliku: {e}")
        return

    if not has_header:
        df.columns = range(df.shape[1])

    max_index = max(x_col_index, y_col_index)
    if df.shape[1] <= max_index:
        parent.statusBar().showMessage(
            f"Błąd: Plik ma tylko {df.shape[1]} kolumn. Wymagane indeksy X ({x_col_index}) lub Y ({y_col_index}) są poza zakresem."
        )
        return

    x_raw = pd.to_numeric(df.iloc[:, x_col_index], errors='coerce').values
    x_distance = x_raw - x_raw[0]

    y = pd.to_numeric(df.iloc[:, y_col_index], errors='coerce').values

    if has_header:
        y_axis_title = str(df.columns[y_col_index])
    else:
        y_axis_title = f"Wartości Y (Kolumna {y_col_index})"

    plot_view.set_data(x_distance, y, y_axis_title)

    start_lat = getattr(parent, "profile_start_x", None)
    start_lon = getattr(parent, "profile_start_y", None)
    azimuth = getattr(parent, "profile_azimuth", 90.0)

    if start_lat is None or start_lon is None:
        parent.statusBar().showMessage("Profil wczytany, ale brak współrzędnych startowych!")
        return

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