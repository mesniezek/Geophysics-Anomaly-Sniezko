from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtWebEngineWidgets import QWebEngineView
import folium
import io

class MapView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()
        view = QWebEngineView()
        m = folium.Map(location=[50.07217314126216, 19.94379250849782], zoom_start=50)
        data = io.BytesIO()
        m.save(data, close_file=False)
        view.setHtml(data.getvalue().decode())
        layout.addWidget(view)
        self.setLayout(layout)
