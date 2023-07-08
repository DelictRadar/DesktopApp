import sys
import time
from PyQt6.QtCore import Qt, QTimer, QDateTime, QTime
from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
import cv2
from PIL import Image
from PIL.ImageQt import ImageQt

from multiprocessing import Process, Pipe
import pickle
from server import server
import winsound

output = None

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SENTINEL")
        self.setWindowIcon(QIcon("./assets/img/Sentinel.ico"))

        self.setStyleSheet("background-color: #222222;")
        self.showMaximized()  # Abrir ventana maximizada

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        # Crear un objeto VideoWriter
        self.fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Codec de compresión de video
        self.fps = 20  # Cuadros por segundo del video

        self.existDetection = True
        self.disableBorderRecording = False
        self.detectionTime = QTime.currentTime()

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
        self.timer.start(20)

        self.capture = cv2.VideoCapture(0)  # Inicializar captura de la cámara

        # Creacion de pipes
        self.client_pipe, self.server_pipe = Pipe()

        # Iniciar el proceso servidor
        self.server_process = Process(target=server, args=(self.server_pipe,))
        self.server_process.start()

        self.show()
    
    def record_evidence(self, rgb_image):
        global output
        current_datetime = QDateTime.currentDateTime()
        timestamp = current_datetime.toString("yyyyMMdd_HHmmss")
        output_file = f"./videos/{timestamp}.mp4"
        output = cv2.VideoWriter(output_file, self.fourcc, self.fps, (int(self.capture.get(3)), int(self.capture.get(4))))
        output.write(rgb_image)

    def alert_detection(self, rgb_image):
        global output
        # Pintar bordes rojos, grabar evidencia y alertar
        if self.disableBorderRecording and self.existDetection:
            self.image_label.setStyleSheet("background-color: #FFFFFF; border: 4px solid #EE1D23;")
            self.detectionTime = QTime.currentTime()
            self.disableBorderRecording = False
            winsound.PlaySound('./assets/sounds/alert-1.wav', winsound.SND_ASYNC)
            self.record_evidence(rgb_image)

        elif not self.disableBorderRecording:
            elapsed_seconds = self.detectionTime.secsTo(QTime.currentTime())
            if output is not None:
                output.write(rgb_image)
            if elapsed_seconds >= 10:
                self.disableBorderRecording = True
                self.image_label.setStyleSheet("background-color: #FFFFFF;")
                if output is not None:
                    output.release()
                    output = None

    def update_image(self):
        global output
        ret, frame = self.capture.read()  # Leer un frame de la cámara
        if ret:
            start_time = time.time()
            # Enviar la imagen capturada al servidor a través del PIPE
            self.client_pipe.send(pickle.dumps(frame))

            # Recibir la imagen resultante del servidor a través del PIPE
            rgb_image, self.existDetection = pickle.loads(self.client_pipe.recv())

            # Alertar detección
            self.alert_detection(cv2.cvtColor(rgb_image, cv2.COLOR_BGR2RGB))

            pil_image = Image.fromarray(rgb_image)  # Convertir a imagen PIL
            qimage = ImageQt(pil_image)  # Convertir a QImage
            pixmap = QPixmap.fromImage(qimage)  # Convertir a QPixmap
            display_width = int(self.width() * 0.7)  # Ancho del display_widget
            display_height = int(self.height() * 0.7)  # Alto del display_widget
            scaled_pixmap = pixmap.scaled(display_width, display_height, Qt.AspectRatioMode.KeepAspectRatio)
            self.image_label.setPixmap(scaled_pixmap)  # Mostrar la imagen capturada

            current_datetime = QDateTime.currentDateTime().toString("hh:mm:ss - yyyy/MM/dd")
            self.datetime_label.setText(current_datetime)
            end_time = time.time()
            print(end_time - start_time)

    def toggle_panel(self):
        if self.panel_visible:
            self.centralWidget().layout().itemAt(1).widget().hide()  # Ocultar el panel_widget
            self.panel_visible = False
        else:
            self.centralWidget().layout().itemAt(1).widget().show()  # Mostrar el panel_widget
            self.panel_visible = True

    def closeEvent(self, event):
        self.capture.release()  # Liberar la cámara al cerrar la ventana
        self.client_pipe.close() # Cerrar el PIPE antes de terminar el cliente
        self.server_process.terminate() # Terminal el proceso servidor
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec())
