from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QLineEdit, QPushButton, QMessageBox
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from pyproj import Transformer
import os

# noinspection PyUnresolvedReferences
class CoordinateSystemDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Współrzędne geograficzne i ich układ")
        self.setFixedSize(450, 350)

        layout = QVBoxLayout()
        header_layout = QHBoxLayout()

        label = QLabel("Wybierz układ współrzędnych:")
        header_layout.addWidget(label)

        self.help_icon = QLabel()

        current_dir = os.path.dirname(__file__)
        project_root = os.path.dirname(current_dir)
        icon_path = os.path.join(project_root, "icons", "question.png")

        pixmap = QPixmap(icon_path)

        if not pixmap.isNull():
            scaled_pixmap = pixmap.scaled(20, 20, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.help_icon.setPixmap(scaled_pixmap)
        else:
            self.help_icon.setText("<b>(?)</b>")
            self.help_icon.setStyleSheet("color: #0078d7;")

        self.help_icon.setFixedSize(20, 20)
        self.help_icon.setCursor(Qt.WhatsThisCursor)

        help_text = (
            "Uwaga: wpisuj liczby w formacie odpowiednim dla układu.\n"
            "PUWG 1992 [EPSG:2180] (np. 244242.50, 567041.75)\n"
            "PUWG 2000 [EPSG:2176-2179] (np. 5547819.82, 7423887.83)\n"
            "WGS84 sz./dł. geogr. (np. 50.06, 19.94)\n"
            "*Przykładowe wartości dla Krakowa w nawiasach."
        )
        self.help_icon.setToolTip(help_text)

        header_layout.addStretch()
        header_layout.addWidget(self.help_icon)
        layout.addLayout(header_layout)

        self.select_box = QComboBox()
        self.select_box.addItems(["PUWG 1992", "PUWG 2000", "WGS84"])
        self.select_box.currentIndexChanged.connect(self.on_crs_changed)
        layout.addWidget(self.select_box)

        self.zone_label = QLabel("Wybierz strefę PUWG 2000:")
        layout.addWidget(self.zone_label)
        self.zone_box = QComboBox()
        self.zone_box.addItems(["Strefa 5 (15°E)", "Strefa 6 (18°E)", "Strefa 7 (21°E)", "Strefa 8 (24°E)"])
        self.zone_box.setCurrentIndex(1)
        layout.addWidget(self.zone_box)

        self.zone_label.hide()
        self.zone_box.hide()

        label_azimuth = QLabel("Azymut profilu (w stopniach, N=0, E=90, S=180, W=270):")
        layout.addWidget(label_azimuth)
        self.azimuth_edit = QLineEdit()
        self.azimuth_edit.setPlaceholderText("Azymut (np. 90.0 dla E)")
        self.azimuth_edit.setText("90.0")
        layout.addWidget(self.azimuth_edit)

        label_start = QLabel("Punkt początkowy (X / Y):")
        layout.addWidget(label_start)
        self.start_x = QLineEdit()
        self.start_x.setPlaceholderText("X start")
        layout.addWidget(self.start_x)

        self.start_y = QLineEdit()
        self.start_y.setPlaceholderText("Y start")
        layout.addWidget(self.start_y)

        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept)
        layout.addWidget(ok_button)

        self.setLayout(layout)

    def on_crs_changed(self, index):
        if index == 1:
            self.zone_label.show()
            self.zone_box.show()
        else:
            self.zone_label.hide()
            self.zone_box.hide()


def convert_to_wgs84(x, y, crs_name, zone_index=None):
    if crs_name == "WGS84":
        return x, y

    elif crs_name == "PUWG 1992":
        transformer = Transformer.from_crs("EPSG:2180", "EPSG:4326", always_xy=True)
        lon, lat = transformer.transform(y, x)
        return lat, lon

    elif crs_name == "PUWG 2000":
        zone_to_epsg = {
            0: "EPSG:2176",
            1: "EPSG:2177",
            2: "EPSG:2178",
            3: "EPSG:2179"
        }
        if zone_index is None:
            zone_index = 1

        epsg_code = zone_to_epsg.get(zone_index, "EPSG:2177")
        transformer = Transformer.from_crs(epsg_code, "EPSG:4326", always_xy=True)
        lon, lat = transformer.transform(y, x)
        return lat, lon

    return x, y


def open_coordinate_system_dialog(parent):
    dialog = CoordinateSystemDialog()
    if dialog.exec_():
        selection = dialog.select_box.currentText()
        x_start_str = dialog.start_x.text()
        y_start_str = dialog.start_y.text()
        azimuth_str = dialog.azimuth_edit.text()
        zone_index = dialog.zone_box.currentIndex() if selection == "PUWG 2000" else None

        fields_to_validate = {
            "X start": x_start_str,
            "Y start": y_start_str,
            "Azymut": azimuth_str
        }

        parsed_values = {}
        try:
            for name, value_str in fields_to_validate.items():
                cleaned_str = value_str.replace(',', '.')
                parsed_values[name] = float(cleaned_str)

        except ValueError:
            QMessageBox.critical(
                dialog,
                "Błąd wprowadzania danych",
                f"Wartość '{value_str}' podana dla pola '{name}' nie jest poprawną liczbą."
                f"\nProszę sprawdzić, czy używasz kropki jako separatora dziesiętnego (np. 50.123).",
                QMessageBox.Ok
            )
            return open_coordinate_system_dialog(parent)

        x_start = parsed_values["X start"]
        y_start = parsed_values["Y start"]
        azimuth = parsed_values["Azymut"]

        try:
            lat_wgs84, lon_wgs84 = convert_to_wgs84(x_start, y_start, selection, zone_index)
        except Exception as e:
            QMessageBox.critical(
                dialog,
                "Błąd konwersji współrzędnych",
                f"Nie udało się przekonwertować współrzędnych: {str(e)}\n"
                f"Sprawdź poprawność wprowadzonych wartości.",
                QMessageBox.Ok
            )
            return open_coordinate_system_dialog(parent)

        zone_info = ""
        if selection == "PUWG 2000":
            zone_names = ["Strefa 5 (15°E)", "Strefa 6 (18°E)", "Strefa 7 (21°E)", "Strefa 8 (24°E)"]
            zone_info = f", {zone_names[zone_index]}"

        message = (
            f"Wybrano: {selection}{zone_info}, "
            f"początek profilu: ({x_start}, {y_start}), "
            f"azymut: {azimuth}°"
        )

        if selection != "WGS84":
            message += f"\nPrzekształcono na WGS84: ({lat_wgs84:.6f}, {lon_wgs84:.6f})"

        parent.profile_crs = selection
        parent.profile_crs_zone = zone_index if selection == "PUWG 2000" else None
        parent.profile_start_x = lat_wgs84
        parent.profile_start_y = lon_wgs84
        parent.profile_azimuth = azimuth

        parent.profile_start_x_original = x_start
        parent.profile_start_y_original = y_start

        parent.statusBar().showMessage(message)