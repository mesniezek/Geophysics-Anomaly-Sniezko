import os
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QComboBox, QPushButton, QLineEdit, QMessageBox, QFileDialog
from logic import profile_import
from ui.raster_calibration import RasterCalibrationDialog

# noinspection PyUnresolvedReferences
class ImportDialog(QDialog):
    def __init__(self, parent=None, plot_view=None, ask_delta=False, locked_type=None):
        super().__init__(parent)
        self.parent_win = parent
        self.plot_view = plot_view
        self.ask_delta = ask_delta
        self.setWindowTitle("Import danych")
        self.setFixedWidth(380)

        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Wybierz typ danych do importu:"))
        self.select_box = QComboBox()
        self.select_box.addItems(["Plik .csv", "Plik .dat", "Plik rastrowy (.png, .jpg)"])
        if locked_type:
            if locked_type == "raster":
                self.select_box.model().item(0).setEnabled(False)
                self.select_box.model().item(1).setEnabled(False)
                self.select_box.setCurrentIndex(2)
            else:
                self.select_box.model().item(2).setEnabled(False)
                self.select_box.setCurrentIndex(0)

        self.select_box.currentIndexChanged.connect(self.toggle_fields)
        layout.addWidget(self.select_box)

        self.delta_label = QLabel("Delta [metry] od poprzedniego profilu:")
        self.delta_edit = QLineEdit("5.0")
        self.ref_label = QLabel("Delta podana jest od profilu:")
        self.delta_ref_box = QComboBox()
        self.delta_ref_box.addItems(["Ostatnio dodanego (przesunięcie relatywne)", "Pierwszego (przesunięcie absolutne)"])

        layout.addWidget(self.delta_label)
        layout.addWidget(self.delta_edit)
        layout.addWidget(self.ref_label)
        layout.addWidget(self.delta_ref_box)

        self.raster_info = QLabel("<b>Parametry fizyczne profilu:</b>")
        self.max_x_label = QLabel("Maksymalny dystans (oś OX) [m]:")
        self.max_x_edit = QLineEdit("15.0")
        self.max_y_label = QLabel("Maksymalna głębokość (oś OY) [m]:")
        self.max_y_edit = QLineEdit("1.9")
        self.threshold_label = QLabel("Próg anomalii głębokich [m]:")
        self.threshold_edit = QLineEdit("1.2")

        layout.addWidget(self.raster_info)
        layout.addWidget(self.max_x_label)
        layout.addWidget(self.max_x_edit)
        layout.addWidget(self.max_y_label)
        layout.addWidget(self.max_y_edit)
        layout.addWidget(self.threshold_label)
        layout.addWidget(self.threshold_edit)

        self.ok_button = QPushButton("Dalej / Importuj")
        self.ok_button.clicked.connect(self.accept)
        layout.addWidget(self.ok_button)

        self.toggle_fields(self.select_box.currentIndex())

    def get_selection(self):
        return self.select_box.currentText()

    def get_delta(self):
        return getattr(self, 'delta_edit', QLineEdit("0.0")).text()

    def get_delta_reference(self):
        return getattr(self, 'delta_ref_box', QComboBox()).currentIndex()

    def toggle_fields(self, index):
        is_raster = (index == 2)
        show_delta = self.ask_delta
        self.delta_label.setVisible(show_delta)
        self.delta_edit.setVisible(show_delta)
        self.ref_label.setVisible(show_delta)
        self.delta_ref_box.setVisible(show_delta)

        self.raster_info.setVisible(is_raster)
        self.max_x_label.setVisible(is_raster)
        self.max_x_edit.setVisible(is_raster)
        self.max_y_label.setVisible(is_raster)
        self.max_y_edit.setVisible(is_raster)
        self.threshold_label.setVisible(is_raster)
        self.threshold_edit.setVisible(is_raster)


def open_import_dialog(parent, plot_view, delta_default=None):
    ask_delta = delta_default is not None

    locked_type = None
    if ask_delta:
        if parent.raster_view.isVisible():
            locked_type = "raster"
        elif parent.plot_view.isVisible():
            locked_type = "data"

    while True:
        dialog = ImportDialog(parent=parent, plot_view=plot_view, ask_delta=ask_delta, locked_type=locked_type)
        if dialog.exec_() != QDialog.Accepted:
            return

        selection = dialog.get_selection()

        delta_value = 0.0
        delta_reference = 0
        if ask_delta:
            try:
                delta_value = float(dialog.get_delta().replace(',', '.'))
                delta_reference = dialog.get_delta_reference()
            except ValueError:
                QMessageBox.critical(parent, "Błąd", "Wartość delty musi być liczbą.")
                continue

        if "rastrowy" in selection:
            file_path, _ = QFileDialog.getOpenFileName(parent, "Wybierz obraz profilu", "", "Obrazy (*.jpg *.png *.jpeg)")
            if file_path:
                calib_win = RasterCalibrationDialog(file_path, os.path.basename(file_path))
                if calib_win.exec_() == QDialog.Accepted:
                    params = {
                        "corners": calib_win.corners,
                        "max_x": float(dialog.max_x_edit.text().replace(',', '.')),
                        "max_y": float(dialog.max_y_edit.text().replace(',', '.')),
                        "threshold": float(dialog.threshold_edit.text().replace(',', '.')),
                        "delta": delta_value,
                        "delta_ref": delta_reference
                    }
                    parent.switch_to_raster(file_path, params)
            return
        else:
            parent.raster_view.hide()
            parent.plot_view.show()

            profile_import.import_profile_data(parent, plot_view, delta_value, delta_reference, selection)
            return