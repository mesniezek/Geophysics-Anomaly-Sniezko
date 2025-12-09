from PyQt5.QtWidgets import QMainWindow, QAction, QSplitter
from PyQt5.QtCore import Qt

from profiles.plot_view import PlotView
from maps.map_view import MapView
from logic import data_loader, georef

# noinspection PyUnresolvedReferences
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.anomaly_mode = False
        self.setWindowTitle("Analiza anomalii geofizycznych - prototyp")
        self.setGeometry(200, 150, 1200, 700)

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
        import_action.triggered.connect(lambda: data_loader.open_import_dialog(self, self.plot_view))
        plik_menu.addAction(import_action)

        add_anomaly_action = QAction("Nałóż anomalie", self)
        add_anomaly_action.triggered.connect(self.enable_anomaly_mode)
        plik_menu.addAction(add_anomaly_action)

    def _setup_central_widget(self):
        splitter = QSplitter(Qt.Horizontal)

        self.plot_view = PlotView(self)
        self.map_view = MapView(self)

        splitter.addWidget(self.plot_view)
        splitter.addWidget(self.map_view)

        self.setCentralWidget(splitter)

    def enable_anomaly_mode(self):
        self.anomaly_mode = True
        self.setWindowTitle("TRYB NAKŁADANIA ANOMALII — kliknij na wykres (Enter aby wyjść)")
        self.statusBar().showMessage("Tryb nakładania anomalii: kliknij na wykres aby dodać punkt.")

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Enter or event.key() == Qt.Key_Return:
            self.anomaly_mode = False
            self.setWindowTitle("Analiza anomalii geofizycznych - prototyp")
            self.statusBar().showMessage("Gotowy")
