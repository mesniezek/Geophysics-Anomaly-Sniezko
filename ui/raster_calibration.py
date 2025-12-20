from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QGraphicsView, QGraphicsScene
from PyQt5.QtGui import QPixmap, QPen, QColor
from PyQt5.QtCore import Qt

class RasterCalibrationDialog(QDialog):
    def __init__(self, image_path, filename):
        super().__init__()
        self.setWindowTitle(f"Importowany profil {filename}")
        self.corners = []
        self.labels = ["Lewy górny (0,0)", "Lewy dolny (0, max głęb.)", "Prawy dolny (max dyst., max głęb.)", "Prawy górny (max dyst., 0)"]

        layout = QVBoxLayout(self)
        self.info = QLabel(f"<b>Krok 1:</b> Kliknij w narożnik: <span style='color:red'>{self.labels[0]}</span>")
        layout.addWidget(self.info)

        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        pixmap = QPixmap(image_path)
        self.scene.addPixmap(pixmap)

        self.view.mousePressEvent = self.on_click
        layout.addWidget(self.view)
        self.setWindowState(Qt.WindowMaximized)

    def on_click(self, event):
        if len(self.corners) < 4:
            pos = self.view.mapToScene(event.pos())
            self.corners.append(pos)
            self.scene.addEllipse(pos.x() - 4, pos.y() - 4, 8, 8, QPen(QColor("red")), QColor("yellow"))

            if len(self.corners) < 4:
                self.info.setText(
                    f"<b>Krok {len(self.corners) + 1}:</b> Kliknij w: <span style='color:red'>{self.labels[len(self.corners)]}</span>")
            else:
                self.accept()