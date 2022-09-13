from flask import Flask,render_template, Response, request, send_from_directory,redirect, url_for
from camera import VideoCamera
import os
import itertools
import time
import test1

app = Flask(__name__)
pi_camera = VideoCamera(flip=False)

@app.route('/', methods = ['GET'])
def index():
    return render_template('index.html') #you can customze index.html here

def gen(camera):
    #get camera frame
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen(pi_camera),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/sys_status')
def sys_status():
    return Response(str(test1.msg_attitude()),
                    mimetype='multipart/x-mixed-replace; boundary=text')

@app.route('/Connected')
def conected():
    test1.wait_conn()
    msg_attitude = str(test1.msg_attitude())
    return render_template('conected.html', attitude=msg_attitude)

@app.route('/Arming')
def arming():
    #test1.force_arm()
    msg_attitude = str(test1.msg_attitude())
    return render_template('arming.html', attitude=msg_attitude)

@app.route('/Disarm')
def disarm():
    msg_attitude = str(test1.msg_attitude())
    render_template('conected.html', attitude=msg_attitude)

@app.route('/test.html')
def test():
    if request.headers.get('accept') == 'text/event-stream':
        def events():
            for i, c in enumerate(itertools.cycle('\|/-')):
                yield "data: %s %d\n\n" % (c, i)
                time.sleep(.1)  # an artificial delay
        return Response(events(), content_type='text/event-stream')
    return redirect(url_for(filename='test.html'))

if __name__ == '__main__':
    app.run(host='192.168.63.12', port=8000)
