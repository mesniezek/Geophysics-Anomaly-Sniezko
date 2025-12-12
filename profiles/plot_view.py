from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget, QVBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import math

# noinspection PyUnresolvedReferences
class PlotView(QWidget):
    anomaly_clicked = pyqtSignal(float)

    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)

        self.canvas = FigureCanvasQTAgg(Figure())
        self.ax = self.canvas.figure.add_subplot(111)

        layout.addWidget(self.canvas)

        self.canvas.mpl_connect("button_press_event", self.on_click)

        self.ax.set_title("Wykres amplitudy")
        self.ax.set_xlabel("Odległość [m]")
        self.ax.set_ylabel("Amplituda")

    def on_click(self, event):
        main = self.window()

        if not getattr(main, "anomaly_mode", False):
            return

        if event.button != 1 or event.xdata is None:
            return

        x_val = float(event.xdata)

        start_lat = getattr(main, "profile_start_x", None)
        start_lon = getattr(main, "profile_start_y", None)
        azimuth = getattr(main, "profile_azimuth", 90.0)

        if start_lat is None or start_lon is None:
            main.statusBar().showMessage("Brak współrzędnych georeferencji!")
            return

        angle_rad = math.radians(azimuth)

        distance = x_val

        dx_lat_meters = distance * math.cos(angle_rad)
        dy_lon_meters = distance * math.sin(angle_rad)

        total_delta = sum(getattr(main, "profile_deltas", [0]))

        perp_angle_rad = math.radians(azimuth + 90)

        perp_lat_meters = total_delta * math.cos(perp_angle_rad)
        perp_lon_meters = total_delta * math.sin(perp_angle_rad)

        meter_to_deg_lat = 1 / 111320
        meter_to_deg_lon = 1 / (111320 * math.cos(math.radians(start_lat)))

        anomaly_lat = start_lat
        anomaly_lon = start_lon

        anomaly_lat += dx_lat_meters * meter_to_deg_lat
        anomaly_lon += dy_lon_meters * meter_to_deg_lon

        anomaly_lat += perp_lat_meters * meter_to_deg_lat
        anomaly_lon += perp_lon_meters * meter_to_deg_lon

        main.map_view.add_anomaly(anomaly_lat, anomaly_lon)

        main.statusBar().showMessage(
            f"Dodano anomalie w X={round(x_val, 2)} m → GPS: ({round(anomaly_lat, 6)}, {round(anomaly_lon, 6)})"
        )

    def set_data(self, x, y, y_axis_title="Wartości Y"):
        try:
            self.ax.clear()
            self.ax.set_title("Wykres amplitudy")
            self.ax.set_xlabel("Odległość od pierwszego punktu [m]")
            self.ax.set_ylabel(y_axis_title)

            self.ax.plot(x, y, "b-")

            self.ax.relim()
            self.ax.autoscale_view()
            self.canvas.draw()
        except Exception as e:
            try:
                parent = self.parent()
                if hasattr(parent, "statusBar"):
                    parent.statusBar().showMessage(f"Błąd rysowania wykresu: {e}")
            except Exception:
                pass
            raise