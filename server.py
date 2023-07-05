import time
import numpy as np
import onnxruntime
from multiprocessing import Pipe, Process
import os
import pickle
import cv2
import random

class ImageProcessor:
    def __init__(self, model_path):
        providers = [
            ('CUDAExecutionProvider', {
                'device_id': 0,
                'arena_extend_strategy': 'kNextPowerOfTwo',
                'gpu_mem_limit': 2 * 1024 * 1024 * 1024,
                'cudnn_conv_algo_search': 'EXHAUSTIVE',
                'do_copy_in_default_stream': True,
            }),
            'CPUExecutionProvider',
        ]

        self.session = onnxruntime.InferenceSession(model_path, providers=providers)
        self.input_name = self.session.get_inputs()[0].name
        self.output_name = self.session.get_outputs()[0].name

        self.names = ['pistol']
        self.colors = {name:[random.randint(0, 255) for _ in range(3)] for i,name in enumerate(self.names)}


    # Resize input to inference
    def letterbox(self, im, new_shape=(640, 640), color=(114, 114, 114), auto=True, scaleup=True, stride=32):
        # Resize and pad image while meeting stride-multiple constraints
        shape = im.shape[:2]  # current shape [height, width]
        if isinstance(new_shape, int):
            new_shape = (new_shape, new_shape)

        # Scale ratio (new / old)
        r = min(new_shape[0] / shape[0], new_shape[1] / shape[1])
        if not scaleup:  # only scale down, do not scale up (for better val mAP)
            r = min(r, 1.0)

        # Compute padding
        new_unpad = int(round(shape[1] * r)), int(round(shape[0] * r))
        dw, dh = new_shape[1] - new_unpad[0], new_shape[0] - new_unpad[1]  # wh padding

        if auto:  # minimum rectangle
            dw, dh = np.mod(dw, stride), np.mod(dh, stride)  # wh padding

        dw /= 2  # divide padding into 2 sides
        dh /= 2

        if shape[::-1] != new_unpad:  # resize
            im = cv2.resize(im, new_unpad, interpolation=cv2.INTER_LINEAR)
        top, bottom = int(round(dh - 0.1)), int(round(dh + 0.1))
        left, right = int(round(dw - 0.1)), int(round(dw + 0.1))
        im = cv2.copyMakeBorder(im, top, bottom, left, right, cv2.BORDER_CONSTANT, value=color)  # add border
        return im, r, (dw, dh)

    def process_image(self, img):
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        image = img.copy()
        image, ratio, dwdh = self.letterbox(image, auto=False)
        image = image.transpose((2, 0, 1))
        image = np.expand_dims(image, 0)
        image = np.ascontiguousarray(image)

        im = image.astype(np.float32)
        im /= 255

        inf_start = time.time()
        output_data = self.session.run([self.output_name], {self.input_name: im})[0]
        inf_end = time.time()

        print(inf_end - inf_start)

        ori_images = [img.copy()]

        for i,(batch_id,x0,y0,x1,y1,cls_id,score) in enumerate(output_data):
            image = ori_images[int(batch_id)]
            box = np.array([x0,y0,x1,y1])
            box -= np.array(dwdh*2)
            box /= ratio
            box = box.round().astype(np.int32).tolist()
            cls_id = int(cls_id)
            score = round(float(score),3)
            name = self.names[cls_id]
            color = self.colors[name]
            name += ' '+str(score)
            cv2.rectangle(image,box[:2],box[2:],color,2)

            if (box[1] >= 15):
                cv2.putText(image,name,(box[0], box[1] - 2),cv2.FONT_HERSHEY_SIMPLEX,0.75,[225, 255, 255],thickness=2)  
            else:
                cv2.putText(image,name,(box[0], box[1] + 20),cv2.FONT_HERSHEY_SIMPLEX,0.75,[225, 255, 255],thickness=2)  

        return ori_images[0]

def server(pipe):
    # Leer la ruta del modelo desde la variable de entorno
    model_path = os.getenv('MODELO_ONNX')

    # Verificar si se proporcionó una ruta válida del modelo
    if model_path is None or not os.path.isfile(model_path):
        print("Ruta del modelo ONNX no especificada o inválida.")
        return

    # Crear instancia de ImageProcessor con la ruta del modelo
    processor = ImageProcessor(model_path)

    while True:
        try:
            # Recibir imagen a través de la tubería
            image = pickle.loads(pipe.recv())

            # Procesar la imagen utilizando la instancia de ImageProcessor
            output = processor.process_image(image)

            # Enviar el resultado de la inferencia a través de la tubería
            pipe.send(pickle.dumps(output))
        except EOFError:
            break
