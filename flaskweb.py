from flask import Flask,render_template, Response, request, send_from_directory,redirect, url_for,stream_with_context
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

def testing1(camera):
        while True :
            frame = camera.get_frame()
            attitude = str(test1.msg_attitude())
            roll_position=attitude.find('roll')
            pitch_position=attitude.find('pitch')
            yaw_position=attitude.find('yaw')
            rollspeed_position=attitude.find('rollspeed')

            roll = float(attitude[roll_position+7:pitch_position-2])
            pitch = float(attitude[pitch_position+8:yaw_position-2])
            yaw = float(attitude[yaw_position+6:rollspeed_position-2])
            yield roll,pitch,yaw,(b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@app.route('/testing1')
def testing():
    return Response(stream_template('testing1.html', data=testing1(pi_camera)),mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/video_feed')
def video_feed():
    return Response(gen(pi_camera),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/Connected')
def conected():
    test1.wait_conn()
    return render_template('connected.html')

@app.route('/Arming')
def arming():
    #test1.force_arm()
    msg_attitude = str(test1.msg_attitude())
    return render_template('arming.html', attitude=msg_attitude)

@app.route('/Disarm')
def disarm():
    msg_attitude = str(test1.msg_attitude())
    render_template('conected.html', attitude=msg_attitude)

@app.route('/xx')
def xx():
    def g():
        attitude = str(test1.msg_attitude())
        while True :
            attitude = str(test1.msg_attitude())
            time.sleep(.01)  # an artificial delay
            yield attitude
    return Response(stream_template('xx.html', data=g()))


def stream_template(template_name, **context):
    app.update_template_context(context)
    t = app.jinja_env.get_template(template_name)
    rv = t.stream(context)
    # uncomment if you don't need immediate reaction
    ##rv.enable_buffering(5)
    return rv

@app.route('/sys_status_stream')
def sys_status_stream():
    def g():
        while True :
            attitude = str(test1.msg_attitude())
            roll_position=attitude.find('roll')
            pitch_position=attitude.find('pitch')
            yaw_position=attitude.find('yaw')
            rollspeed_position=attitude.find('rollspeed')

            roll = float(attitude[roll_position+7:pitch_position-2])
            pitch = float(attitude[pitch_position+8:yaw_position-2])
            yaw = float(attitude[yaw_position+6:rollspeed_position-2])
            yield roll,pitch,yaw
    return Response(stream_template('sys_status_stream.html', data=g()))

if __name__ == '__main__':
    app.run(host='192.168.63.12', port=8000)
