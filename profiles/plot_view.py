from PyQt5.QtWidgets import QWidget, QVBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure


class PlotView(QWidget):
    """
    Widżet wyświetlający wykresy za pomocą Matplotlib.
    Zawiera logikę do ustawiania i odświeżania danych profilu.
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)

        # Stworzenie obszaru rysowania (Canvas) i figury Matplotlib
        self.canvas = FigureCanvasQTAgg(Figure())
        # Dodanie podwykresu (osi) do figury
        self.ax = self.canvas.figure.add_subplot(111)

        # Ustawienie domyślnych etykiet i tytułu
        self.ax.set_title("Wykres amplitudy")
        self.ax.set_xlabel("Odległość od pierwszego punktu [m]")
        self.ax.set_ylabel("Amplituda")

        layout.addWidget(self.canvas)

    def set_data(self, x, y):
        """
        Czyści aktualny wykres i rysuje nowy profil (x, y).

        :param x: Dane dla osi X (Odległość od pierwszego punktu).
        :param y: Dane dla osi Y (Amplituda).
        """
        self.ax.clear()  # Wyczyść poprzedni wykres

        # Ponowne ustawienie tytułu i etykiet po czyszczeniu
        self.ax.set_title("Wykres amplitudy")
        self.ax.set_xlabel("Odległość od pierwszego punktu [m]")
        self.ax.set_ylabel("Amplituda")

        # Rysowanie danych (linia niebieska)
        self.ax.plot(x, y, "b-")

        # Automatyczne skalowanie osi do nowych danych
        self.ax.autoscale(enable=True, axis='both', tight=False)

        self.canvas.draw()  # Odświeżenie widoku