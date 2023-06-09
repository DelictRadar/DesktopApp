import cv2
import random
import numpy as np
import onnxruntime as ort
from PIL import Image, ImageTk
from tkinter import Tk, Label, StringVar, OptionMenu, Frame, CENTER, W, E, Button
import tkinter.font as TkFont
import device
import winsound

from datetime import datetime

import time

print_count = 0
freeze_detection = 0
isRecording = False

# TKinter set up

## Window
win = Tk()
win['background'] = '#222222'
win.iconbitmap("../assets/img/Sentinel.ico")
win.title("SENTINEL")
win.state("zoomed")

## Label of Video
alert_border = Frame(win, background="red")
input_label = Label(win,  borderwidth=0)
input_label.place(relx=0.5, rely=0.5, anchor=CENTER)

## Label of Detect
detect_label = Label(win, borderwidth=0)

## Button
def stop_alert():
    winsound.PlaySound('../assets/sounds/nosound.wav', 
                       winsound.SND_PURGE + winsound.SND_ASYNC) 

stop_button = Button(win,
    bg="#044A59",
    fg="white",
    text="Cancelar Alerta",
    borderwidth=0,
    padx=10,
    pady=5,
    font=TkFont.Font(family="Roboto", weight="bold", size=20),
    command=stop_alert)

## Var for Dropdown
var = StringVar(win)
var.set("Select a Video Camera")

## Device list
device_list = device.getDeviceList()
device_index = []
index = 0

for camera in device_list:
    device_index.append('{}: {}'.format(str(index), camera))
    index+=1

## Dropdown
def change_device(choice):
    choice = int(var.get().split(':')[0])
    global cap
    cap = cv2.VideoCapture(choice)

dd= OptionMenu(win, var, *device_index, command=change_device)
dd.grid(row=0, column=0)
dd.config(width=100)
dd.place(relx=0.5, rely=0.01, anchor=CENTER)
dd['background'] = '#222222'
dd['foreground'] = 'white'
dd["highlightthickness"]=0
dd['font'] 

# OnnxRuntime set up
w = "../assets/model_0.65_0.75.onnx"
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
session = ort.InferenceSession(w, providers=providers)

# OpenCV set up
cap = cv2.VideoCapture(0)

# Resize input to inference
def letterbox(im, new_shape=(640, 640), color=(114, 114, 114), auto=True, scaleup=True, stride=32):
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

names = ['pistol']
colors = {name:[random.randint(0, 255) for _ in range(3)] for i,name in enumerate(names)}

pistol_detected = False

def show_detect(img):
    scale_percent = 70
    width = int(img.shape[1] * scale_percent / 100)
    height = int(img.shape[0] * scale_percent / 100)
    dim = (width, height)
  
    # resize image
    resized = cv2.resize(img, dim, interpolation = cv2.INTER_AREA) 

    return resized

forcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
recording = any

def handle_detect(ori_images, fr_width, fr_height):
    global pistol_detected
    global freeze_detection
    global forcc
    global recording
    global isRecording

    if pistol_detected and freeze_detection == 0:
        # Modiying the place of labels and buttons
        input_label.place(relx=0.6, rely=0.5, anchor=E)
        detect_label.place(relx=0.6, rely=0.5, anchor=W)
        stop_button.place(relx=0.75, rely=0.9, anchor=W)

        dct_img = Image.fromarray(show_detect(ori_images[0]))
        dct_imgtk = ImageTk.PhotoImage(image = dct_img)
        detect_label.imgtk = dct_imgtk
        detect_label.configure(image=dct_imgtk)

        input_label.config(highlightbackground="red", highlightthickness=5)
        winsound.PlaySound('../assets/sounds/alert-1.wav', winsound.SND_ASYNC)

         
        isRecording = True
        recordPath = '../videos/' + datetime.today().strftime('%Y%m%d_%H%M%S')  + '.mp4'
        recording = cv2.VideoWriter(recordPath, forcc, 15.0, (fr_width, fr_height))


def show_frames():
    start = time.time()
    global pistol_detected

    _, img = cap.read()

    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    image = img.copy()
    image, ratio, dwdh = letterbox(image, auto=False)
    image = image.transpose((2, 0, 1))
    image = np.expand_dims(image, 0)
    image = np.ascontiguousarray(image)

    im = image.astype(np.float32)
    im /= 255

    outname = [i.name for i in session.get_outputs()]

    inname = [i.name for i in session.get_inputs()]

    inp = {inname[0]:im}

    global print_count
    global freeze_detection
    global recording
    global isRecording

    outputs = []

    inf_end = 0
    inf_start = 0

    inf_start = time.time()
    outputs = session.run(outname, inp)[0]
    inf_end = time.time()

    ori_images = [img.copy()]
 
    for i,(batch_id,x0,y0,x1,y1,cls_id,score) in enumerate(outputs):
        image = ori_images[int(batch_id)]
        box = np.array([x0,y0,x1,y1])
        box -= np.array(dwdh*2)
        box /= ratio
        box = box.round().astype(np.int32).tolist()
        cls_id = int(cls_id)
        score = round(float(score),3)
        name = names[cls_id]
        color = colors[name]
        name += ' '+str(score)
        cv2.rectangle(image,box[:2],box[2:],color,2)

        #Handle Detection
        pistol_detected = True

        if (box[1] >= 15):
            cv2.putText(image,name,(box[0], box[1] - 2),cv2.FONT_HERSHEY_SIMPLEX,0.75,[225, 255, 255],thickness=2)  
        else:
            cv2.putText(image,name,(box[0], box[1] + 20),cv2.FONT_HERSHEY_SIMPLEX,0.75,[225, 255, 255],thickness=2)  

    handle_detect(ori_images, int(cap.get(3)), int(cap.get(4)))

    if not pistol_detected or freeze_detection == 160:
        pistol_detected = False
        freeze_detection = 0
        input_label.config(highlightthickness=0)
        detect_label.place_forget()
        stop_button.place_forget()
        input_label.place(relx=0.5, rely=0.5, anchor=CENTER)
        if isRecording:
            recording.release()
            isRecording = False
        
    else:
        recording.write(cv2.cvtColor(ori_images[0], cv2.COLOR_BGR2RGB))
        freeze_detection += 1

    # Show real-time images
    inp_img = Image.fromarray(ori_images[0])
    imgtk = ImageTk.PhotoImage(image = inp_img)
    input_label.imgtk = imgtk
    input_label.configure(image=imgtk)

    # Repeat after x ms
    end = time.time()

    if(print_count == 80):
        print(f"Inference time:\t\t{round(inf_end - inf_start, 5)} sec")
        print(f"Frame processing time:\t{round(end - start, 5)} sec\n")
        print_count = 0
    else:
        print_count += 1

    input_label.after(20, show_frames)

show_frames()
win.mainloop()