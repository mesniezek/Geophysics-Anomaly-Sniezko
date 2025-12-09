from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QComboBox, QPushButton
from logic import csv_import


class ImportDialog(QDialog):
    """
    Ogólne okno dialogowe do wyboru typu danych do importu.
    Aktualnie obsługuje przekierowanie tylko do importu CSV.
    """
    def __init__(self, parent=None, plot_view=None):
        super().__init__(parent)
        self.plot_view = plot_view # Przekazanie referencji do PlotView

        self.setWindowTitle("Import danych")
        self.setFixedSize(300, 150)

        layout = QVBoxLayout(self)

        label = QLabel("Wybierz typ danych do importu:")
        layout.addWidget(label)

        # Lista dostępnych typów danych
        self.select_box = QComboBox()
        self.select_box.addItems(["Plik .csv", "Plik .dat", "Plik rastrowy (.png, .img)"])
        layout.addWidget(self.select_box)

        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept)
        layout.addWidget(ok_button)

    def get_selection(self):
        """Zwraca wybrany typ pliku."""
        return self.select_box.currentText()


def open_import_dialog(parent, plot_view):
    """
    Otwiera główne okno dialogowe importu i deleguje zadanie
    do odpowiedniej funkcji w zależności od wyboru.
    """
    dialog = ImportDialog(parent=parent, plot_view=plot_view)
    if dialog.exec_() != QDialog.Accepted:
        return

    selection = dialog.get_selection()

    if selection == "Plik .csv":
        # Przekierowanie do specyficznego dialogu importu CSV
        csv_import.open_csv_import_dialog(parent, plot_view)
    else:
        # Obsługa dla typów plików, których obsługa jest w przygotowaniu
        parent.statusBar().showMessage(f"Wybrano: {selection} (obsługa w przygotowaniu)")