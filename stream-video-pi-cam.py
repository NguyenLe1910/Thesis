import io
import picamera
import logging
import socketserver
from threading import Condition
from http import server
import test1

BeginPAGE="""\
<html>
<head>
<title>Thesis-V2.0</title>
</head>
<body>
<center><h1>Thesis-V2.0</h1></center>
<center><img src="stream.mjpg" width="640" height="480"></center>
</body>
<body>
    <form action="/thesis2.0/Arming">
      <button type="submit" name="ForceArm" value="true"> Force Arm </button>
   </form>
</body>
</html>
"""
ArmingPAGE="""\
<html>
<head>
<title>Thesis-V2.0-</title>
</head>
<body>
<center><h1>Thesis-V2.0</h1></center>
<center><img src="stream.mjpg" width="640" height="480"></center>
<center> The vehicle is Arming
</body>
<body>
    <form action="/thesis2.0">
      <button type="submit" name="Disarm" value="true"> Disarm </button>
   </form>
</body>
</html>
"""
DisarmPAGE="""\
<html>
<head>
<title>Thesis-V2.0</title>
</head>
<body>
<center><h1>Thesis-V2.0</h1></center>
<center><img src="stream.mjpg" width="640" height="480"></center>
</body>
<body>
    <form action="/thesis2.0/Disarm">
      <button type="submit" name="ForceArm" value="true"> Force Arm </button>
   </form>
</body>
</html>
"""
class StreamingOutput(object):
    def __init__(self):
        self.frame = None
        self.buffer = io.BytesIO()
        self.condition = Condition()

    def write(self, buf):
        if buf.startswith(b'\xff\xd8'):
            # New frame, copy the existing buffer's content and notify all
            # clients it's available
            self.buffer.truncate()
            with self.condition:
                self.frame = self.buffer.getvalue()
                self.condition.notify_all()
            self.buffer.seek(0)
        return self.buffer.write(buf)

class StreamingHandler(server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(301)
            self.send_header('Location', '/thesis2.0')
            self.end_headers()
        elif self.path == '/thesis2.0':
            content = BeginPAGE.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(content))
            if self.path.find("ForceArm=true") != -1:
                print("Run Force Arm")
                test1.force_arm()
            self.end_headers()
            self.wfile.write(content)
        elif self.path.find('Arming') > -1:
            content = ArmingPAGE.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(content))
            if self.path.find("ForceArm=true") != -1:
                print("Run Force Arm")
                test1.force_arm()
            #do whatever you want
            self.end_headers()
            self.wfile.write(content)
        elif self.path == '/thesis2.0/Disarm':
            content = DisarmPAGE.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(content))
            if self.path.find("Disarm=true") != -1:
                print("Disarm")
            #do whatever you want
            self.end_headers()
            self.wfile.write(content)
        elif self.path == '/stream.mjpg':
            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            try:
                while True:
                    with output.condition:
                        output.condition.wait()
                        frame = output.frame
                    self.wfile.write(b'--FRAME\r\n')
                    self.send_header('Content-Type', 'image/jpeg')
                    self.send_header('Content-Length', len(frame))
                    self.end_headers()
                    self.wfile.write(frame)
                    self.wfile.write(b'\r\n')
            except Exception as e:
                logging.warning(
                    'Removed streaming client %s: %s',
                    self.client_address, str(e))      
        else:
            self.send_error(404)
            self.end_headers()
            #do whatever you want

class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True

with picamera.PiCamera(resolution='640x480', framerate=24) as camera:
    output = StreamingOutput()
    #Uncomment the next line to change your Pi's Camera rotation (in degrees)
    #camera.rotation = 90
    camera.start_recording(output, format='mjpeg')
    try:
        address = ('', 8160)
        test1.connect()
        server = StreamingServer(address, StreamingHandler)
        server.serve_forever()
    finally:
        camera.stop_recording() 