from PyQt5.QtWidgets import QMainWindow, QAction, QSplitter
from PyQt5.QtCore import Qt

from profiles.plot_view import PlotView
from maps.map_view import MapView
from logic import data_loader, georef


class MainWindow(QMainWindow):
    """
    Główne okno aplikacji. Łączy widok wykresu (PlotView) i mapy (MapView) za pomocą QSplitter.
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Analiza anomalii geofizycznych - prototyp")
        self.setGeometry(200, 150, 1200, 700)

        self._setup_menubar()  # Konfiguracja paska menu
        self._setup_central_widget()  # Konfiguracja głównego widżetu

        self.statusBar().showMessage("Gotowy")

    def _setup_menubar(self):
        """
        Konfiguruje pasek menu i akcje.
        """
        menubar = self.menuBar()
        plik_menu = menubar.addMenu("Plik")

        # Akcja Importuj
        import_action = QAction("Importuj", self)
        # Połączenie akcji z otwarciem dialogu importu danych
        import_action.triggered.connect(
            lambda: data_loader.open_import_dialog(self, self.plot_view)
        )
        plik_menu.addAction(import_action)

        # Akcja Układ współrzędnych
        coordinate_system_action = QAction("Układ współrzędnych", self)
        # Połączenie akcji z otwarciem dialogu układu współrzędnych
        coordinate_system_action.triggered.connect(
            lambda: georef.open_coordinate_system_dialog(self)
        )
        plik_menu.addAction(coordinate_system_action)

    def _setup_central_widget(self):
        """
        Konfiguruje centralny widżet z QSplitterem dla PlotView i MapView.
        """
        splitter = QSplitter(Qt.Horizontal)  # Splitter poziomy

        # Inicjalizacja widoków
        self.plot_view = PlotView(self)
        self.map_view = MapView(self)

        # Dodanie widoków do splittera
        splitter.addWidget(self.plot_view)
        splitter.addWidget(self.map_view)

        self.setCentralWidget(splitter)