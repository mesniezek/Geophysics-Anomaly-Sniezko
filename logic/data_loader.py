from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QComboBox, QPushButton, QLineEdit, QMessageBox
from logic import profile_import

# noinspection PyUnresolvedReferences
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
        return getattr(self, 'delta_edit', QLineEdit("0.0")).text()

    def get_delta_reference(self):
        return getattr(self, 'delta_ref_box', QComboBox()).currentIndex()


def open_import_dialog(parent, plot_view, delta_default=None):
    ask_delta = delta_default is not None

    while True:
        dialog = ImportDialog(parent=parent, plot_view=plot_view, ask_delta=ask_delta)
        if dialog.exec_() != QDialog.Accepted:
            return

        selection = dialog.get_selection()

        if ask_delta:
            delta_str = dialog.get_delta()
            delta_reference = dialog.get_delta_reference()

            try:
                cleaned_str = delta_str.replace(',', '.')
                delta_value = float(cleaned_str)

            except ValueError:
                QMessageBox.critical(
                    parent,
                    "Błąd wprowadzania delty",
                    f"Wartość '{delta_str}' podana dla Delty nie jest poprawną liczbą."
                    f"\nProszę używać kropki jako separatora dziesiętnego (np. 5.5).",
                    QMessageBox.Ok
                )
                continue
        else:
            delta_value = 0.0
            delta_reference = 0

        if selection in ["Plik .csv", "Plik .dat"]:
            profile_import.import_profile_data(parent, plot_view, delta_value, delta_reference, selection)
            return
        else:
            parent.statusBar().showMessage(f"Wybrano: {selection} (obsługa w przygotowaniu)")
            return