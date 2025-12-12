from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QComboBox, QLineEdit, QPushButton

class CoordinateSystemDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Współrzędne geograficzne i ich układ")
        self.setFixedSize(450, 400)

        layout = QVBoxLayout()

        label = QLabel("Wybierz układ współrzędnych:")
        layout.addWidget(label)

        self.select_box = QComboBox()
        self.select_box.addItems(["WGS84", "2000", "Brak - lokalny"])
        layout.addWidget(self.select_box)

        format_label = QLabel("Uwaga: wpisuj liczby w formacie 50.123456 (z kropką)")
        layout.addWidget(format_label)

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

        label_end = QLabel("Punkt końcowy (X / Y) (opcjonalnie):")
        layout.addWidget(label_end)
        self.end_x = QLineEdit()
        self.end_x.setPlaceholderText("X koniec")
        layout.addWidget(self.end_x)

        self.end_y = QLineEdit()
        self.end_y.setPlaceholderText("Y koniec")
        layout.addWidget(self.end_y)

        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept)
        layout.addWidget(ok_button)

        self.setLayout(layout)


def open_coordinate_system_dialog(parent):
    dialog = CoordinateSystemDialog()
    if dialog.exec_():
        selection = dialog.select_box.currentText()
        x_start_str = dialog.start_x.text()
        y_start_str = dialog.start_y.text()
        azimuth_str = dialog.azimuth_edit.text()
        x_end = dialog.end_x.text()
        y_end = dialog.end_y.text()

        try:
            x_start = float(x_start_str)
            y_start = float(y_start_str)
            azimuth = float(azimuth_str)
        except ValueError:
            parent.statusBar().showMessage("Błąd: X, Y i Azymut muszą być liczbami w formacie 50.123456.")
            return

        message = (
            f"Wybrano: {selection}, "
            f"początek profilu: ({x_start}, {y_start}), "
            f"azymut: {azimuth}°, "
            f"koniec profilu: ({x_end}, {y_end})."
        )

        parent.profile_crs = selection
        parent.profile_start_x = x_start
        parent.profile_start_y = y_start
        parent.profile_azimuth = azimuth

        parent.statusBar().showMessage(message)