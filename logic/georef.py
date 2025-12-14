from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QComboBox, QLineEdit, QPushButton, QMessageBox


# noinspection PyUnresolvedReferences
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
        x_end_str = dialog.end_x.text()
        y_end_str = dialog.end_y.text()

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

        message = (
            f"Wybrano: {selection}, "
            f"początek profilu: ({x_start}, {y_start}), "
            f"azymut: {azimuth}°, "
            f"koniec profilu: ({x_end_str}, {y_end_str})."
        )

        parent.profile_crs = selection
        parent.profile_start_x = x_start
        parent.profile_start_y = y_start
        parent.profile_azimuth = azimuth

        parent.statusBar().showMessage(message)