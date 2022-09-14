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

def stream_template(template_name, **context):
    app.update_template_context(context)
    t = app.jinja_env.get_template(template_name)
    rv = t.stream(context)
    # uncomment if you don't need immediate reaction
    ##rv.enable_buffering(5)
    return rv

@app.route('/video_feed')
def video_feed():
    return Response(gen(pi_camera),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/Connected')
def conected():
    test1.wait_conn()
    def g():
        attitude = str(test1.msg_attitude())
        while True :
            attitude = str(test1.msg_attitude())
            time.sleep(.2)  # an artificial delay
            yield attitude
    return Response(stream_template('conected.html', data=g()))

@app.route('/Arming')
def arming():
    #test1.force_arm()
    msg_attitude = str(test1.msg_attitude())
    return render_template('arming.html', attitude=msg_attitude)

@app.route('/Disarm')
def disarm():
    msg_attitude = str(test1.msg_attitude())
    render_template('conected.html', attitude=msg_attitude)


@app.route('/testxxx')
def testxxx():
    def g():
        attitude = str(test1.msg_attitude())
        while True :
            attitude = str(test1.msg_attitude())
            time.sleep(.01)  # an artificial delay
            yield attitude
    return Response(stream_template('test.html', data=g()))
    
if __name__ == '__main__':
    app.run(host='192.168.63.12', port=8000)
