from flask import Flask,render_template, Response, request
from camera import VideoCamera
import os
import itertools
import time
import test1

app = Flask(__name__)
pi_camera = VideoCamera(flip=False)

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
            fix_type = int(GPS[fix_type_position+11])

            latitude_position = GPS.find('lat')
            lontitude_position = GPS.find('lon')
            altitude_position = GPS.find('alt')
            eph_position = GPS.find('eph')
            epv_position = GPS.find('epv')
            vel_position = GPS.find('vel')
            cog_position = GPS.find('cog')
            satellites_visible_position	= GPS.find('satellites_visible')
            alt_ellipsoid_position = GPS.find('alt_ellipsoid ')
                
            lat = float(GPS[latitude_position+6:lontitude_position-2])
            lon = float(GPS[lontitude_position+6:altitude_position-2])
            alt = float(GPS[altitude_position+6:eph_position-2])
            eph	= float(GPS[eph_position+6:epv_position-2])
            epv = float(GPS[epv_position+6:vel_position-2])
            vel = float(GPS[vel_position+6:cog_position-2])
            cog = float(GPS[cog_position+6:satellites_visible_position-2])
            satellites_visible = float(GPS[satellites_visible_position+21:alt_ellipsoid_position-2])
                
            yield roll,pitch,yaw,fix_type,lat,lon,alt,eph,epv,vel,cog,satellites_visible

@app.route('/video_feed')
def video_feed():
    return Response(gen(pi_camera),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
def index():
    return render_template('index.html') #you can customze index.html here

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
    return Response(stream_template('connected.html', data=sys_status_needed()))


@app.route('/Arming')
def arming():
    try:
        test1.force_arm()
        return Response(stream_template('arming.html', data=sys_status_needed()))
    except:
        return Response(stream_template('connected.html', data=sys_status_needed()))
    
@app.route('/Disarm')
def disarm():
    return Response(stream_template('connected.html', data=sys_status_needed()))


@app.route('/sys_status_stream',methods =["GET","POST"])
def sys_status_stream():
    data = request.get_json()
    print(data)
    return Response(stream_template('sys_status_stream.html', data=sys_status_needed()))
 
if __name__ == '__main__':
    app.run(host='192.168.63.12', port=8000)
