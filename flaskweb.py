from flask import Flask
from camera import VideoCamera
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html') #you can customze index.html here




if __name__ == '__main__':
    app.run(host='192.168.63.12', port=8000)
