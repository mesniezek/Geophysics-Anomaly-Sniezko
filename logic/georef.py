from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QComboBox, QLineEdit, QPushButton


class CoordinateSystemDialog(QDialog):
    """
    Okno dialogowe do ustawiania układu współrzędnych geograficznych
    i wprowadzania współrzędnych punktów początkowego i końcowego profilu.
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Współrzędne geograficzne i ich układ")
        self.setFixedSize(450, 300)

        layout = QVBoxLayout()

        # Wybór układu współrzędnych
        label = QLabel("Wybierz układ współrzędnych:")
        layout.addWidget(label)

        self.select_box = QComboBox()
        self.select_box.addItems(["WGS84", "2000", "Brak - lokalny"])  # Przykładowe systemy
        layout.addWidget(self.select_box)

        # Wprowadzanie punktu początkowego
        label_start = QLabel("Punkt początkowy (X / Y):")
        layout.addWidget(label_start)
        self.start_x = QLineEdit()
        self.start_x.setPlaceholderText("X start")
        layout.addWidget(self.start_x)

        self.start_y = QLineEdit()
        self.start_y.setPlaceholderText("Y start")
        layout.addWidget(self.start_y)

        # Wprowadzanie punktu końcowego
        label_end = QLabel("Punkt końcowy (X / Y):")
        layout.addWidget(label_end)
        self.end_x = QLineEdit()
        self.end_x.setPlaceholderText("X koniec")
        layout.addWidget(self.end_x)

        self.end_y = QLineEdit()
        self.end_y.setPlaceholderText("Y koniec")
        layout.addWidget(self.end_y)

        # Przycisk OK
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept)
        layout.addWidget(ok_button)

        self.setLayout(layout)


def open_coordinate_system_dialog(parent):
    """
    Otwiera okno dialogowe wyboru układu współrzędnych i wyświetla
    wybrane dane w pasku statusu rodzica.
    """
    dialog = CoordinateSystemDialog()
    if dialog.exec_():
        # Pobranie danych z dialogu po akceptacji
        selection = dialog.select_box.currentText()
        x_start = dialog.start_x.text()
        y_start = dialog.start_y.text()
        x_end = dialog.end_x.text()
        y_end = dialog.end_y.text()

        # Formatowanie wiadomości i wyświetlenie jej w status barze
        message = f"Wybrano: {selection}, początek profilu: ({x_start}, {y_start}), koniec profilu: ({x_end}, {y_end})."
        parent.statusBar().showMessage(message)