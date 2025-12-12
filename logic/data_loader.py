from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QComboBox, QPushButton, QLineEdit
from logic import csv_import


class ImportDialog(QDialog):
    def __init__(self, parent=None, plot_view=None, ask_delta=False):
        super().__init__(parent)
        self.plot_view = plot_view
        self.delta_value = 0.0

        self.setWindowTitle("Import danych")
        self.setFixedSize(300, 250 if ask_delta else 150)

        layout = QVBoxLayout(self)

        label = QLabel("Wybierz typ danych do importu:")
        layout.addWidget(label)

        self.select_box = QComboBox()
        self.select_box.addItems(["Plik .csv", "Plik .dat", "Plik rastrowy (.png, .img)"])
        layout.addWidget(self.select_box)

        if ask_delta:
            delta_label = QLabel("Delta [metry] od poprzedniego profilu:")
            layout.addWidget(delta_label)
            self.delta_edit = QLineEdit()
            self.delta_edit.setText("5")
            layout.addWidget(self.delta_edit)

            ref_label = QLabel("Delta podana jest od profilu:")
            layout.addWidget(ref_label)
            self.delta_ref_box = QComboBox()
            self.delta_ref_box.addItems(
                ["Ostatnio dodanego (przesunięcie relatywne)", "Pierwszego (przesunięcie absolutne)"])
            layout.addWidget(self.delta_ref_box)

        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept)
        layout.addWidget(ok_button)

    def get_selection(self):
        return self.select_box.currentText()

    def get_delta(self):
        try:
            return float(getattr(self, 'delta_edit', QLineEdit("0.0")).text())
        except Exception:
            return 0.0

    def get_delta_reference(self):
        return getattr(self, 'delta_ref_box', QComboBox()).currentIndex()


def open_import_dialog(parent, plot_view, delta=None):
    ask_delta = delta is not None
    dialog = ImportDialog(parent=parent, plot_view=plot_view, ask_delta=ask_delta)
    if dialog.exec_() != QDialog.Accepted:
        return

    selection = dialog.get_selection()
    delta_value = dialog.get_delta() if ask_delta else 0.0
    delta_reference = dialog.get_delta_reference() if ask_delta else 0

    if selection == "Plik .csv":
        csv_import.open_csv_import_dialog(parent, plot_view, delta_value, delta_reference)
    else:
        parent.statusBar().showMessage(f"Wybrano: {selection} (obsługa w przygotowaniu)")