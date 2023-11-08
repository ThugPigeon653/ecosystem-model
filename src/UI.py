import sys  
import os
from PyQt5.QtWidgets import QApplication, QWidget, QLabel
from PyQt5.QtGui import QPixmap, QPainter
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtWidgets import QDesktopWidget 
import world_visualizer
import threading
import json

class CustomWidget(QWidget):
    __visualizer_utils: world_visualizer.AnimalData = None
    __conn = None

    def __init__(self, background_path, overlay_folder):
        super().__init__()
        self.__visualizer_utils = world_visualizer.AnimalData()
        self.background_image = QPixmap(background_path)
        self.overlay_images = []
        self.overlay_positions = []

        for root, dirs, files in os.walk(overlay_folder):
            for file in files:
                if file.lower().endswith(".png"):
                    overlay_path = os.path.join(root, file)
                    overlay_image = QPixmap(overlay_path)
                    self.overlay_images.append(overlay_image)
                    self.overlay_positions.append(QPoint(0, 0))
        screen = QDesktopWidget().screenGeometry()
        self.original_background_size = self.background_image.size()
        self.background_image = self.background_image.scaled(screen.width(), screen.height(), Qt.KeepAspectRatio)
        self.setFixedSize(screen.width(), screen.height())
        self.setMouseTracking(True)
        self.text_label = QLabel(self)
        self.text_label.setGeometry(self.original_background_size.width(), 0, self.width() - self.original_background_size.width(), self.height())
        self.text_label.setAlignment(Qt.AlignCenter)
        self.text_label.setStyleSheet("QLabel { font-size: 24px; background-color: white; }")

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(QPoint(0, 0), self.background_image)
        for i, overlay_image in enumerate(self.overlay_images):
            overlay_image = overlay_image.scaled(self.original_background_size)
            painter.drawPixmap(self.overlay_positions[i], overlay_image)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            terrain_size = self.original_background_size
            click_pos = event.pos()

            for i, overlay_position in enumerate(self.overlay_positions):
                overlay_image = self.overlay_images[i]
                if overlay_image.rect().contains(click_pos):
                    pixel_color = overlay_image.toImage().pixel(click_pos)
                    alpha = (pixel_color >> 24) & 0xFF
                    if alpha != 0:
                        area = self.__visualizer_utils.get_animals_by_region(i)
                        self.text_label.setText(f"{str(area)}\nToday: {self.get_today()}")

    @staticmethod
    def get_today()->int:
        with open('config/shared_runtime_config.json', 'r') as file:
            config = world_visualizer.json.load(file)
        try:
            today=config['today']
        except Exception as e: 
            today=None
        return today
            

def background_thread():
    import ecosystem as eco
    eco.initialize()

if __name__ == "__main__":
    # reset the shared config file
    with open('config/shared_runtime_config.json', 'r') as file:
        config = json.load(file)
        config["today"]=0
        with open('config/shared_runtime_config.json', 'w') as file:
            json.dump(config, file, indent=4)
    island=world_visualizer.Island()
    world_visualizer.MapUtils().draw_ocean()
    task=threading.Thread(target=background_thread)
    task.start()
    app = QApplication(sys.argv)
    #background_path = "color_blocks/color_block_1.png"
    background_path ="img/ocean/0.png"
    """for i in range(30):
        __conn = sqlite3.connect('animal_database.db')
        cursor = __conn.cursor()
        cursor.execute('SELECT name FROM terrain WHERE id = ?', (i,))   
        name=cursor.fetchone()
        print(f"terrain: {name}  index: {i}")

    """
    overlay_folder = "split_color_blocks"
    window = CustomWidget(background_path, overlay_folder)
    window.showFullScreen()
    sys.exit(app.exec_())
