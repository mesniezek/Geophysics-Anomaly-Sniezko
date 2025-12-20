from PyQt5.QtWidgets import QScrollArea, QLabel, QFrame
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt


class RasterView(QScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWidgetResizable(False)
        self.setFrameShape(QFrame.NoFrame)
        self.container = QLabel()
        self.container.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.setWidget(self.container)
        self.container.mousePressEvent = self.handle_click

        self.calib_data = None
        self.scale_factor = 1.0

    def set_raster(self, image_path, params):
        self.calib_data = params
        original_pixmap = QPixmap(image_path)

        target_height = self.height() if self.height() > 100 else 600

        scaled_pixmap = original_pixmap.scaledToHeight(target_height, Qt.SmoothTransformation)

        self.scale_factor = scaled_pixmap.height() / original_pixmap.height()

        self.container.setPixmap(scaled_pixmap)
        self.container.setFixedSize(scaled_pixmap.size())

    def handle_click(self, event):
        main = self.window()
        if not getattr(main, "anomaly_mode", False) or not self.calib_data:
            return

        pos_x = event.pos().x() / self.scale_factor
        pos_y = event.pos().y() / self.scale_factor

        c = self.calib_data['corners']
        width_px = c[2].x() - c[0].x()
        height_px = c[1].y() - c[0].y()

        rel_x = (pos_x - c[0].x()) / width_px
        rel_y = (pos_y - c[0].y()) / height_px

        rel_x = max(0, min(1, rel_x))
        rel_y = max(0, min(1, rel_y))

        dist_m = rel_x * self.calib_data['max_x']
        depth_m = rel_y * self.calib_data['max_y']
        is_deep = depth_m > self.calib_data['threshold']

        main.add_anomaly_from_raster(dist_m, depth_m, is_deep)