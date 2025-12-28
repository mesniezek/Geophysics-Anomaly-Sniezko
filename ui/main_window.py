from PyQt5.QtWidgets import QMainWindow, QAction, QSplitter
from PyQt5.QtCore import Qt

from profiles.plot_view import PlotView
from maps.map_view import MapView
from logic import data_loader, georef
from profiles.raster_view import RasterView
from ui.anomaly_points_dialog import AnomalyPointsDialog
import numpy as np
import math
import folium

# noinspection PyUnresolvedReferences
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.anomaly_mode = False
        self.profile_start_x = 50.07217314126216
        self.profile_start_y = 19.94379250849782
        self.profile_deltas = []
        self.all_connections = []  # Lista przechowująca narysowane linie
        self.setWindowTitle("Analiza anomalii geofizycznych - prototyp")
        self.setGeometry(200, 150, 1200, 700)
        self.anomaly_points = []

        self._setup_menubar()
        self._setup_central_widget()

        self.statusBar().showMessage("Gotowy")

    def _setup_menubar(self):
        menubar = self.menuBar()
        plik_menu = menubar.addMenu("Plik")

        coordinate_system_action = QAction("Układ współrzędnych", self)
        coordinate_system_action.triggered.connect(lambda: georef.open_coordinate_system_dialog(self))
        plik_menu.addAction(coordinate_system_action)

        import_action = QAction("Importuj nowy profil", self)
        import_action.triggered.connect(lambda: data_loader.open_import_dialog(self, self.plot_view))
        plik_menu.addAction(import_action)

        import_action = QAction("Importuj kolejny profil", self)
        import_action.triggered.connect(lambda: data_loader.open_import_dialog(self, self.plot_view, 3))
        plik_menu.addAction(import_action)

        add_anomaly_action = QAction("Nałóż anomalie", self)
        add_anomaly_action.triggered.connect(self.enable_anomaly_mode)
        plik_menu.addAction(add_anomaly_action)

        points_menu = plik_menu.addMenu("Punkty")
        all_points_act = QAction("Wszystkie", self)
        all_points_act.triggered.connect(lambda: self.show_anomaly_points("all"))
        points_menu.addAction(all_points_act)

        shallow_points_act = QAction("Płytkie", self)
        shallow_points_act.triggered.connect(lambda: self.show_anomaly_points("PŁYTKA"))
        points_menu.addAction(shallow_points_act)

        deep_points_act = QAction("Głębokie", self)
        deep_points_act.triggered.connect(lambda: self.show_anomaly_points("GŁĘBOKA"))
        points_menu.addAction(deep_points_act)

    def _setup_central_widget(self):
        self.splitter = QSplitter(Qt.Horizontal)

        self.plot_view = PlotView(self)
        self.plot_view.setMinimumSize(450, 450)
        self.raster_view = RasterView(self)
        self.raster_view.hide()

        self.map_view = MapView(self)

        self.splitter.addWidget(self.plot_view)
        self.splitter.addWidget(self.raster_view)
        self.splitter.addWidget(self.map_view)

        self.splitter.setSizes([500, 500, 700])

        self.setCentralWidget(self.splitter)

    def switch_to_raster(self, image_path, params):
        self.plot_view.hide()
        self.raster_view.show()
        self.raster_view.set_raster(image_path, params)

        delta = params.get('delta', 0.0)
        delta_ref = params.get('delta_ref', 0)

        if delta == 0 and not self.profile_deltas:
            self.profile_deltas = [0]
            current_total_delta = 0
        else:
            if delta_ref == 0:
                current_total_delta = sum(self.profile_deltas) + delta
                self.profile_deltas.append(delta)
            else:
                current_total_delta = delta
                self.profile_deltas = [delta]

        fake_distances = np.array([0, params['max_x']])

        self.map_view.draw_profile(
            fake_distances,
            self.profile_start_x,
            self.profile_start_y,
            self.profile_azimuth,
            current_total_delta
        )

        angle_rad = math.radians(self.profile_azimuth)
        perp_angle_rad = math.radians(self.profile_azimuth + 90)
        meter_to_deg_lat = 1 / 111320
        meter_to_deg_lon = 1 / (111320 * math.cos(math.radians(self.profile_start_x)))

        start_lat_shifted = self.profile_start_x + (current_total_delta * math.cos(perp_angle_rad) * meter_to_deg_lat)
        start_lon_shifted = self.profile_start_y + (current_total_delta * math.sin(perp_angle_rad) * meter_to_deg_lon)

        if current_total_delta == 0 or delta_ref == 1:
            self.map_view.map_obj = folium.Map(location=[start_lat_shifted, start_lon_shifted], zoom_start=19)
            self.map_view.draw_profile(fake_distances, self.profile_start_x, self.profile_start_y, self.profile_azimuth,
                                       current_total_delta)

        self.statusBar().showMessage(f"Załadowano profil rastrowy: {params['max_x']}m x {params['max_y']}m")

    def add_anomaly_from_raster(self, dist_m, depth_m, is_deep):
        start_lat = self.profile_start_x
        start_lon = self.profile_start_y
        azimuth = getattr(self, "profile_azimuth", 90.0)

        if start_lat is None or start_lon is None:
            self.statusBar().showMessage("Błąd: Brak współrzędnych georeferencji!")
            return

        angle_rad = math.radians(azimuth)
        dx_lat_meters = dist_m * math.cos(angle_rad)
        dy_lon_meters = dist_m * math.sin(angle_rad)

        total_delta = sum(getattr(self, "profile_deltas", [0]))
        perp_angle_rad = math.radians(azimuth + 90)
        perp_lat_meters = total_delta * math.cos(perp_angle_rad)
        perp_lon_meters = total_delta * math.sin(perp_angle_rad)

        meter_to_deg_lat = 1 / 111320
        meter_to_deg_lon = 1 / (111320 * math.cos(math.radians(start_lat)))

        anomaly_lat = start_lat + (dx_lat_meters + perp_lat_meters) * meter_to_deg_lat
        anomaly_lon = start_lon + (dy_lon_meters + perp_lon_meters) * meter_to_deg_lon

        self.map_view.add_anomaly(anomaly_lat, anomaly_lon)

        type_label = "GŁĘBOKA" if is_deep else "PŁYTKA"
        new_point = {
            "index": len(self.anomaly_points) + 1,
            "lat": anomaly_lat,
            "lon": anomaly_lon,
            "depth": depth_m,
            "type": type_label
        }

        self.anomaly_points.append(new_point)
        self.map_view.add_anomaly(anomaly_lat, anomaly_lon)

        self.statusBar().showMessage(
            f"Dodano anomalię {type_label} (y={round(depth_m, 2)}m) → GPS: ({round(anomaly_lat, 6)}, {round(anomaly_lon, 6)})"
        )

    def enable_anomaly_mode(self):
        self.anomaly_mode = True
        self.setWindowTitle("TRYB NAKŁADANIA ANOMALII — kliknij na wykres (Enter aby wyjść)")
        self.statusBar().showMessage("Tryb nakładania anomalii: kliknij na wykres aby dodać punkt.")

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Enter or event.key() == Qt.Key_Return:
            self.anomaly_mode = False
            self.setWindowTitle("Analiza anomalii geofizycznych - prototyp")
            self.statusBar().showMessage("Gotowy")

    def show_anomaly_points(self, filter_type):
        if not self.anomaly_points:
            self.statusBar().showMessage("Brak zapisanych punktów")
            return

        if filter_type == "all":
            filtered_list = self.anomaly_points
            title_suffix = "Wszystkie"
        else:
            filtered_list = [p for p in self.anomaly_points if p.get("type") == filter_type]
            title_suffix = "Płytkie" if filter_type == "PŁYTKA" else "Głębokie"

        dialog = AnomalyPointsDialog(self, filtered_list)
        dialog.setWindowTitle(f"Punkty - {title_suffix}")

        dialog.show_on_map_requested.connect(self.refresh_map_view)

        dialog.exec_()

    def refresh_map_view(self, points_to_show):
        self.map_view.update_map_with_filters(points_to_show)
        self.statusBar().showMessage(f"Zaktualizowano mapę. Widoczne punkty: {len(points_to_show)}")