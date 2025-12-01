from PyQt5.QtWidgets import QWidget, QVBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure


class PlotView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)

        self.canvas = FigureCanvasQTAgg(Figure())
        self.ax = self.canvas.figure.add_subplot(111)

        self.ax.set_title("Wykres amplitudy")
        self.ax.set_xlabel("Odległość od pierwszego punktu [m]")
        self.ax.set_ylabel("Amplituda")

        layout.addWidget(self.canvas)

    def set_data(self, x, y):
        self.ax.clear()
        self.ax.set_title("Wykres amplitudy")
        self.ax.set_xlabel("Odległość od pierwszego punktu [m]")
        self.ax.set_ylabel("Amplituda")
        self.ax.plot(x, y, "b-")

        self.ax.autoscale(enable=True, axis='both', tight=False)

        self.canvas.draw()