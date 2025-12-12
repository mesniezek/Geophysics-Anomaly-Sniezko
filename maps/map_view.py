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

    def draw_profile(self, distances, start_lat, start_lon, azimuth, total_delta):
        angle_rad = math.radians(azimuth)

        meter_to_deg_lat = 1 / 111320
        meter_to_deg_lon = 1 / (111320 * math.cos(math.radians(start_lat)))

        perp_angle_rad = math.radians(azimuth + 90)

        lat_offset = total_delta * math.cos(perp_angle_rad) * meter_to_deg_lat
        lon_offset = total_delta * math.sin(perp_angle_rad) * meter_to_deg_lon

        points = []
        for d in distances:
            dx_lat_meters = d * math.cos(angle_rad)
            dy_lon_meters = d * math.sin(angle_rad)

            lat_change = dx_lat_meters * meter_to_deg_lat
            lon_change = dy_lon_meters * meter_to_deg_lon

            lat = start_lat + lat_change + lat_offset
            lon = start_lon + lon_change + lon_offset
            points.append((lat, lon))

        if total_delta == 0:
            self.map_obj = folium.Map(location=[points[0][0], points[0][1]], zoom_start=19)

        folium.PolyLine(points, color="blue", weight=4).add_to(self.map_obj)

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