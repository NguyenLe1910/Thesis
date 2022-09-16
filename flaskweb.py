from flask import Flask,render_template, Response, request, send_from_directory,redirect, url_for,stream_with_context,jsonify
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

def sys_status_needed():
        while True :
            attitude = str(test1.msg_attitude())            
            roll_position=attitude.find('roll')
            pitch_position=attitude.find('pitch')
            yaw_position=attitude.find('yaw')
            rollspeed_position=attitude.find('rollspeed')

            roll = float(attitude[roll_position+7:pitch_position-2])
            pitch = float(attitude[pitch_position+8:yaw_position-2])
            yaw = float(attitude[yaw_position+6:rollspeed_position-2])

            GPS = str(test1.msg_GPS_RAW())
            fix_type_position = GPS.find('fix_type')
            print(fix_type_position)
            print(GPS[fix_type_position+12])
            fix_type = int(GPS[fix_type_position+12])
            
            yield roll,pitch,yaw,fix_type

@app.route('/video_feed')
def video_feed():
    return Response(gen(pi_camera),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/joystick')
def joystick():
    return render_template('joystick.html')

def stream_template(template_name, **context):
    app.update_template_context(context)
    t = app.jinja_env.get_template(template_name)
    rv = t.stream(context)
    return rv

@app.route('/Connected')
def conected():
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
    return Response(stream_template('connected.html', data=g()))


@app.route('/Arming')
def arming():
    #test1.force_arm()
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
    return Response(stream_template('arming.html', data=g()))


@app.route('/Disarm')
def disarm():
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
    return Response(stream_template('connected.html', data=g()))


@app.route('/sys_status_stream')
def sys_status_stream():
    return Response(stream_template('sys_status_stream.html', data=sys_status_needed()))

if __name__ == '__main__':
    app.run(host='192.168.63.12', port=8000)
