import sys
import os
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtGui import QPixmap, QPainter
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtWidgets import QDesktopWidget 
import world_visualizer
import sys
import os


import world_visualizer

class CustomWidget(QWidget):
    def __init__(self, background_path, overlay_folder):
        super().__init__()
        self.background_image = QPixmap(background_path)
        self.overlay_images = []
        self.overlay_positions = []

        for root, dirs, files in os.walk(overlay_folder):
            for file in files:
                if file.lower().endswith(".png"):
                    overlay_path = os.path.join(root, file)
                    overlay_image = QPixmap(overlay_path)
                    if overlay_image.isNull():
                        print(f"Failed to load overlay image: {overlay_path}")
                    self.overlay_images.append(overlay_image)
                    self.overlay_positions.append(QPoint(0, 0))
        screen = QDesktopWidget().screenGeometry()
        self.background_image = self.background_image.scaled(screen.width(), screen.height(), Qt.KeepAspectRatio)
        self.setFixedSize(screen.width(), screen.height())
        self.setMouseTracking(True)
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(QPoint(0, 0), self.background_image)
        for i, overlay_image in enumerate(self.overlay_images):
            overlay_image = overlay_image.scaled(self.background_image.size())
            painter.drawPixmap(self.overlay_positions[i], overlay_image)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            for i, overlay_position in enumerate(self.overlay_positions):
                overlay_image = self.overlay_images[i]
                if overlay_image.rect().contains(event.pos()):
                    pixel_color = overlay_image.toImage().pixel(event.pos())
                    alpha = (pixel_color >> 24) & 0xFF
                    if alpha != 0:
                        print(f"Clicked on overlay image {i + 1}")

if __name__ == "__main__":
    #world_visualizer.Island()
    app = QApplication(sys.argv)
    background_path = "color_blocks/color_block_1.png"
    overlay_folder = "split_color_blocks"
    window = CustomWidget(background_path, overlay_folder)
    window.showFullScreen()
    sys.exit(app.exec_())
