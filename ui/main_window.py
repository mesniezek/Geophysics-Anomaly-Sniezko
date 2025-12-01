from PyQt5.QtWidgets import QMainWindow, QAction, QSplitter
from PyQt5.QtCore import Qt

from profiles.plot_view import PlotView
from maps.map_view import MapView
from logic import data_loader, georef


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Analiza anomalii geofizycznych - prototyp")
        self.setGeometry(200, 150, 1200, 700)

        menubar = self.menuBar()
        plik_menu = menubar.addMenu("Plik")

        import_action = QAction("Importuj", self)
        import_action.triggered.connect(
            lambda: data_loader.open_import_dialog(self, self.plot_view)
        )
        plik_menu.addAction(import_action)

        coordinate_system_action = QAction("Układ współrzędnych", self)
        coordinate_system_action.triggered.connect(
            lambda: georef.open_coordinate_system_dialog(self)
        )
        plik_menu.addAction(coordinate_system_action)

        splitter = QSplitter(Qt.Horizontal)
        self.plot_view = PlotView(self)
        self.map_view = MapView(self)

        splitter.addWidget(self.plot_view)
        splitter.addWidget(self.map_view)
        self.setCentralWidget(splitter)

        self.statusBar().showMessage("Gotowy")
