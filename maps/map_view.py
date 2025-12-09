from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtWebEngineWidgets import QWebEngineView
import folium
import io


class MapView(QWidget):
    """
    Widżet wyświetlający interaktywną mapę (za pomocą biblioteki Folium)
    osadzoną w QWebEngineView.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()
        view = QWebEngineView()

        # Inicjalizacja mapy Folium z domyślną lokalizacją (Kraków, Poland)
        # Opcjonalnie: można tu dodać logikę do wyświetlania zaimportowanego profilu
        m = folium.Map(location=[50.07217314126216, 19.94379250849782], zoom_start=50)

        # Konwersja mapy Folium do danych HTML
        data = io.BytesIO()
        m.save(data, close_file=False)

        # Wyświetlenie mapy HTML w widżecie QWebEngineView
        view.setHtml(data.getvalue().decode())
        layout.addWidget(view)
        self.setLayout(layout)