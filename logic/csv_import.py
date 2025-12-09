from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QCheckBox,
    QPushButton, QFileDialog, QHBoxLayout, QLineEdit
)
import pandas as pd


class CsvImportDialog(QDialog):
    """
    Okno dialogowe do wyboru pliku CSV i opcji importu.
    Umożliwia użytkownikowi wybranie pliku i określenie, czy zawiera nagłówki.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Import pliku CSV")
        self.setMinimumWidth(400)

        self.file_path = ""  # Ścieżka do wybranego pliku CSV

        layout = QVBoxLayout(self)

        # Sekcja wyboru pliku
        file_layout = QHBoxLayout()
        self.file_edit = QLineEdit()
        self.file_edit.setReadOnly(True)  # Pole tylko do wyświetlania ścieżki
        browse_btn = QPushButton("Wybierz plik...")
        browse_btn.clicked.connect(self.browse_file)

        file_layout.addWidget(self.file_edit)
        file_layout.addWidget(browse_btn)

        layout.addLayout(file_layout)

        # Checkbox dla nagłówka
        self.header_checkbox = QCheckBox("Plik zawiera nagłówki w pierwszym wierszu")
        self.header_checkbox.setChecked(True)  # Domyślnie zaznaczone
        layout.addWidget(self.header_checkbox)

        # Informacje o oczekiwanej strukturze danych
        info_label = QLabel(
            "Założenie: kolumna 2 = x, kolumna 'amplituda' = oś Y.\n"
            "Ułożenie kolumn jest zawsze takie samo."
        )
        layout.addWidget(info_label)

        # Przyciski OK/Anuluj
        btn_layout = QHBoxLayout()
        ok_btn = QPushButton("OK")
        cancel_btn = QPushButton("Anuluj")
        ok_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)

        layout.addLayout(btn_layout)

    def browse_file(self):
        """
        Otwiera standardowe okno dialogowe do wyboru pliku CSV.
        """
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Wybierz plik CSV",
            "",
            "Pliki CSV (*.csv);;Wszystkie pliki (*.*)"  # Filtry plików
        )
        if path:
            self.file_path = path
            self.file_edit.setText(path)


def open_csv_import_dialog(parent, plot_view):
    """
    Otwiera okno dialogowe importu, wczytuje dane i aktualizuje PlotView.
    Wymaga: rodzica (dla statusBara) i instancji PlotView.
    """
    dialog = CsvImportDialog(parent)
    if dialog.exec_() != QDialog.Accepted:
        return

    if not dialog.file_path:
        parent.statusBar().showMessage("Nie wybrano pliku CSV")
        return

    has_header = dialog.header_checkbox.isChecked()
    sep = ";"  # Domyślny separator CSV

    # Wczytanie pliku za pomocą pandas
    try:
        if has_header:
            # Wczytanie z nagłówkiem, separatorem ';' i przecinkiem jako separatorem dziesiętnym
            df = pd.read_csv(dialog.file_path, sep=sep, decimal=',')
        else:
            # Wczytanie bez nagłówka, kolumny będą numerowane od 0
            df = pd.read_csv(dialog.file_path, sep=sep, header=None, decimal=',')
    except Exception as e:
        parent.statusBar().showMessage(f"Błąd podczas wczytywania pliku: {e}")
        return

    # Walidacja minimalnej liczby kolumn
    if df.shape[1] < 3:
        parent.statusBar().showMessage(
            f"Za mało kolumn w pliku (znaleziono {df.shape[1]}). Oczekiwane minimum: 3."
        )
        return

    # Przygotowanie danych dla osi X
    # Kolumna 2 (indeks 1) to surowe wartości X
    x_raw = pd.to_numeric(df.iloc[:, 1], errors='coerce').values

    # Obliczenie odległości jako przesunięcia względem pierwszego punktu
    x_distance = x_raw - x_raw[0]

    # Przygotowanie danych dla osi Y (Amplituda)
    if has_header and "amplituda" in df.columns:
        # Preferowane użycie kolumny z nazwą 'amplituda'
        y = pd.to_numeric(df["amplituda"], errors='coerce').values
    else:
        # W przeciwnym razie użycie kolumny 3 (indeks 2)
        y = pd.to_numeric(df.iloc[:, 2], errors='coerce').values

    # Ustawienie danych w widoku wykresu
    plot_view.set_data(x_distance, y)
    parent.statusBar().showMessage(f"Załadowano dane z {dialog.file_path}")