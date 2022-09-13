import cv2
import sys
from flask import Flask, render_template, Response
from camera_pi import VideoCamera
from flask_basicauth import BasicAuth
import time
import threading

app = Flask(__name__)

pi_camera = VideoCamera(flip=False)

@app.route('/')
def index():
    return render_template('index.html')

def gen(camera):
    while True:
        if camera.stopped:
            break
        frame = camera.read()
        ret, jpeg = cv2.imencode('.jpg',frame)
        if jpeg is not None:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n\r\n')
        else:
            print("frame is none")

@app.route('/video_feed')
def video_feed():
    return Response(gen(pi_camera),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='192.168.63.12',port=8000)