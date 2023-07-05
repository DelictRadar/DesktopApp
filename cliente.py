import cv2
import os
import pickle
from multiprocessing import Pipe, Process
import signal
from server import server

def client(pipe):
    # Función para manejar la señal de terminación del cliente
    def handle_termination(signal):
        # Cerrar el PIPE
        pipe.close()
        # Detener el proceso servidor
        os.kill(os.getppid(), signal.SIGTERM)

    # Registrar la señal de terminación del cliente
    signal.signal(signal.SIGINT, handle_termination)

    while True:
        # Capturar video de la cámara
        cap = cv2.VideoCapture(0)
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            try:
                # Enviar la imagen capturada al servidor a través del PIPE
                pipe.send(pickle.dumps(frame))

                # Recibir la imagen resultante del servidor a través del PIPE
                result = pickle.loads(pipe.recv())

                # Mostrar la imagen resultante en tiempo real
                result = cv2.cvtColor(result, cv2.COLOR_BGR2RGB)
                cv2.imshow("Resultado del servidor", result)

                if cv2.waitKey(1) == ord('q'):
                    break

            except EOFError:
                print("Mal Cliente")
                break

        # Liberar los recursos de la cámara
        cap.release()
        cv2.destroyAllWindows()

        # Cerrar el PIPE antes de terminar el cliente
        pipe.close()
        break

if __name__ == '__main__':
    # Crear una tubería (Pipe) para la comunicación con el servidor
    client_pipe, server_pipe = Pipe()

    # Iniciar el proceso servidor
    server_process = Process(target=server, args=(server_pipe,))
    server_process.start()

    # Ejecutar el cliente
    client(client_pipe)

    # Esperar a que el proceso servidor termine
    server_process.join()
