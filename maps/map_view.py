from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtWebEngineWidgets import QWebEngineView
import folium
import io
import math

# noinspection PyUnresolvedReferences
class MapView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.profile_history = []

        layout = QVBoxLayout(self)
        self.view = QWebEngineView()

        self.map_obj = folium.Map(
            location=[50.07217314126216, 19.94379250849782],
            zoom_start=19
        )

        self._refresh()
        layout.addWidget(self.view)

    def draw_profile(self, distances, start_lat, start_lon, azimuth, total_delta):
        profile_data = {
            "distances": distances,
            "start_lat": start_lat,
            "start_lon": start_lon,
            "azimuth": azimuth,
            "total_delta": total_delta
        }
        self.profile_history.append(profile_data)

        self._add_profile_to_folium(profile_data)
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

    def highlight_anomaly(self, points, highlight_index):
        for p in points:
            color = "yellow" if p["index"] == highlight_index else "red"
            folium.CircleMarker(
                location=[p["lat"], p["lon"]],
                radius=6,
                color=None,
                fill=True,
                fill_color=color,
                fill_opacity=0.6
            ).add_to(self.map_obj)

        self._refresh()

    def refresh_filtered_points(self, filtered_points):
        self.clear_markers_and_redraw_everything(filtered_points)

    def clear_markers_and_redraw_everything(self, points):
        self.highlight_anomaly(points, -1)

    def _add_profile_to_folium(self, p):
        angle_rad = math.radians(p["azimuth"])
        perp_angle_rad = math.radians(p["azimuth"] + 90)
        meter_to_deg_lat = 1 / 111320
        meter_to_deg_lon = 1 / (111320 * math.cos(math.radians(p["start_lat"])))

        lat_offset = p["total_delta"] * math.cos(perp_angle_rad) * meter_to_deg_lat
        lon_offset = p["total_delta"] * math.sin(perp_angle_rad) * meter_to_deg_lon

        line_points = []
        for d in p["distances"]:
            lat_c = d * math.cos(angle_rad) * meter_to_deg_lat
            lon_c = d * math.sin(angle_rad) * meter_to_deg_lon
            line_points.append((p["start_lat"] + lat_c + lat_offset,
                                p["start_lon"] + lon_c + lon_offset))

        folium.PolyLine(line_points, color="blue", weight=4).add_to(self.map_obj)

    def update_map_with_filters(self, points_to_show):
        import folium

        if not self.profile_history:
            return

        start_p = self.profile_history[0]
        self.map_obj = folium.Map(location=[start_p["start_lat"], start_p["start_lon"]], zoom_start=19)

        for p in self.profile_history:
            self._add_profile_to_folium(p)

        for p in points_to_show:
            folium.CircleMarker(
                location=[p["lat"], p["lon"]],
                radius=6,
                color="red",
                fill=True,
                fill_color="red",
                popup=f"Głębokość: {round(p['depth'], 2)}m"
            ).add_to(self.map_obj)

        self._refresh()