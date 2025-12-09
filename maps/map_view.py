from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtWebEngineWidgets import QWebEngineView
import folium
import io
import math

class MapView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)
        self.view = QWebEngineView()

        self.map_obj = folium.Map(
            location=[50.07217314126216, 19.94379250849782],
            zoom_start=19
        )

        self._refresh()
        layout.addWidget(self.view)

    def draw_profile(self, distances, start_lat, start_lon, delta = 0):
        meter_to_deg = 1 / (111320 * math.cos(math.radians(start_lat)))

        points = []
        for d in distances:
            lon = start_lon + d * meter_to_deg
            lat = start_lat
            points.append((lat, lon))

        self.map_obj = folium.Map(location=[start_lat, start_lon], zoom_start=19)
        folium.PolyLine(points, color="blue", weight=4).add_to(self.map_obj)

        delta_m = 5
        meter_to_deg_lat = 1 / 111320  # przelicznik metrów na stopnie szerokości geograficznej

        # Tworzymy nową listę punktów przesuniętych w pionie
        shifted_points = [(lat + delta_m * meter_to_deg_lat, lon) for lat, lon in points]

        # Rysujemy nowy wykres przesunięty
        folium.PolyLine(shifted_points, color="green", weight=4).add_to(self.map_obj)

        self._refresh()

    def add_anomaly(self, lat, lon):
        folium.CircleMarker(
            location=[lat, lon],
            radius=6,
            color="red",
            fill=True,
            fill_color="red"
        ).add_to(self.map_obj)

        self._refresh()

    def _refresh(self):
        data = io.BytesIO()
        self.map_obj.save(data, close_file=False)
        self.view.setHtml(data.getvalue().decode())
