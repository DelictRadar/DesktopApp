import sys
from PyQt6.QtCore import Qt, QTimer, QDateTime
from PyQt6.QtGui import QPixmap, QColor, QIcon, QPainter, QBrush, QCursor, QPalette
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
import cv2
from PIL import Image
from PIL.ImageQt import ImageQt


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SENTINEL")
        self.setWindowIcon(QIcon("./assets/img/Sentinel.ico"))

        self.setStyleSheet("background-color: #222222;")
        self.showMaximized()  # Abrir ventana maximizada

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)

        display_widget = QWidget(self)
        display_widget.setStyleSheet("background-color: #222222;")
        display_layout = QVBoxLayout(display_widget)
        display_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(display_widget, 7)

        self.image_label = QLabel(display_widget)
        self.image_label.setScaledContents(True)
        self.image_label.setStyleSheet("background-color: #FFFFFF;")
        display_layout.addWidget(self.image_label)

        self.datetime_label = QLabel(display_widget)
        self.datetime_label.setStyleSheet("color: #FFFFFF; font-size: 20px;")
        display_layout.addWidget(self.datetime_label)

        panel_widget = QWidget(self)
        panel_widget.setStyleSheet("background-color: #222222; border-left: 1px solid #444444;")
        panel_layout = QVBoxLayout(panel_widget)
        panel_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        main_layout.addWidget(panel_widget, 3)

        self.panel_visible = True  # Variable para rastrear la visibilidad del panel
        self.toggle_button = QPushButton("Imágenes", display_widget)
        self.toggle_button.setStyleSheet("background-color: #3CC5A6; color: #FFFFFF; font-size: 16px;"
                                         "border-radius: 5px; padding: 5px;")
        self.toggle_button.clicked.connect(self.toggle_panel)
        display_layout.addWidget(self.toggle_button, alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_image)
        self.timer.start(16)  # Actualizar cada 16 ms (aprox. 60 fps)

        self.capture = cv2.VideoCapture(0)  # Inicializar captura de la cámara

        self.show()

    def update_image(self):
        ret, frame = self.capture.read()  # Leer un frame de la cámara
        if ret:
            rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # Convertir a RGB
            pil_image = Image.fromarray(rgb_image)  # Convertir a imagen PIL
            qimage = ImageQt(pil_image)  # Convertir a QImage
            pixmap = QPixmap.fromImage(qimage)  # Convertir a QPixmap
            display_width = int(self.width() * 0.7)  # Ancho del display_widget
            display_height = int(self.height() * 0.7)  # Alto del display_widget
            scaled_pixmap = pixmap.scaled(display_width, display_height, Qt.AspectRatioMode.KeepAspectRatio)
            self.image_label.setPixmap(scaled_pixmap)  # Mostrar la imagen capturada

            current_datetime = QDateTime.currentDateTime().toString("hh:mm:ss - yyyy/MM/dd")
            self.datetime_label.setText(current_datetime)

    def toggle_panel(self):
        if self.panel_visible:
            self.centralWidget().layout().itemAt(1).widget().hide()  # Ocultar el panel_widget
            self.panel_visible = False
        else:
            self.centralWidget().layout().itemAt(1).widget().show()  # Mostrar el panel_widget
            self.panel_visible = True

    def closeEvent(self, event):
        self.capture.release()  # Liberar la cámara al cerrar la ventana
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec())
