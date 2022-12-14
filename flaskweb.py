from flask import Flask,render_template, Response, request, url_for
from camera import VideoCamera
import os
import itertools
import time
import test1

app = Flask(__name__)
app2 = Flask(__name__)
pi_camera = VideoCamera(flip=False)

RC_id =''
RC_x = 0
RC_Vx = 0
RC_y = 0
RC_Vy = 0
RC_button_0 = False

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

def stream_template(template_name, **context):
    app.update_template_context(context)
    t = app.jinja_env.get_template(template_name)
    rv = t.stream(context)
    return rv

@app.route('/Connect')
def conect():
    test1.wait_conn()
    return Response(stream_template('connected.html', data=sys_status_needed()))

@app.route('/Connected')
def conected():
    return Response(stream_template('connected.html', data=sys_status_needed()))

@app.route('/Arming')
def arming():
    test1.force_arm_test()
    return Response(stream_template('arming.html', data=sys_status_needed()))

@app.route('/trytoarm')
def trytoarm():
    test1.arm_test()
    return Response(stream_template('connected.html', data=sys_status_needed()))

@app.route('/Disarm')
def disarm():
    test1.disarm_test()
    return Response(stream_template('connected.html', data=sys_status_needed()))
        
@app.route('/RC_data_stream',methods =["GET","POST"])
def RC_data_stream():
    if request.method == "POST":
        data = str(request.get_json())
        x_position  = data.find('x')
        Vx_position = data.find('Vx')
        y_position  = data.find('y')
        Vy_position = data.find('Vy')        
        RC_id = data[9:x_position-3]
        RC_x  = float(data[x_position+5:x_position+14])
        RC_Vx = float(data[Vx_position+6:Vx_position+14])
        RC_y  = float(data[y_position+5:y_position+14])
        RC_Vy = float(data[Vy_position+6:Vy_position+14])
    return Response(stream_template('RC_data_stream.html', data=sys_status_needed()))

@app.route('/attitude',methods =["GET","POST"])
def attitude():
    return Response(stream_template('attitude.html', data=sys_status_needed()))

if __name__ == '__main__':
    app.run(host='192.168.63.12', port=8000)