# Web streaming example
# Source code from the official PiCamera package
# http://picamera.readthedocs.io/en/latest/recipes2.html#web-streaming

import io
import picamera
import logging
import socketserver
from threading import Condition
from http import server
import test1

HOMEPAGE="""\
<html>
<head>
<title>Thesis2.0 </title>
</head>
<body>
<center><h1>Thesis - 2.0</h1></center>
<center><img src="stream.mjpg" width="640" height="480"></center>
</body>
<br>
<center>
    <form action="/thesis2.0/Connected">
      <button type="submit" name="Connected" value="true"> Connect to USV </button>
   </form>
</center>
<body>
<form action="/thesis2.0/test">
      <button type="submit"> Test </button>
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

class WebServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True

class webHandler(server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(301)
            self.send_header('Location', '/thesis2.0')
            self.end_headers()
        elif self.path.endswith('/stream.mjpg'):
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
        elif self.path == '/thesis2.0':
            content = HOMEPAGE.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
        elif self.path.find('Connected') > -1:
            msg_attitude = str(test1.msg_attitude())    
            content = '<html>'
            content += '<head><title>Thesis2.0 </title></head>'
            content += '<body><center><h1>Thesis - 2.0</h1></center><center><img src="stream.mjpg" width="640" height="480"></center></body>'
            content += '<br>'
            content += msg_attitude
            content += '<center> <form action="/thesis2.0/Connected"> <button type="submit" name="ForceArm" value="true"> Force Arm </button> </form> <center>'
            content += '</html>'
            while True :
                self.send_response(200)
                self.send_header('Content-Type', 'text/html')
                self.send_header('Content-Length', len(content))
                self.end_headers()
                msg_attitude = str(test1.msg_attitude())
                self.wfile.write(content.encode())

        if self.path.find("Connected=true") != -1:
                test1.wait_conn()
        if self.path.find("ForceArm=true") != -1:
                test1.force_arm()
        if self.path.find("Disarm=true") != -1:
                test1.force_arm()


with picamera.PiCamera(resolution='640x480', framerate=24) as camera:
    output = StreamingOutput()
    #Uncomment the next line to change your Pi's Camera rotation (in degrees)
    #camera.rotation = 90
    camera.start_recording(output, format='mjpeg')
    try:
        address = ('', 8160)
        #test1.connect()
        server = WebServer(address, webHandler)
        server.serve_forever()
    finally:
        camera.stop_recording() 
