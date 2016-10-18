import datetime
import os

from flask import Flask
from flask import render_template


app = Flask(__name__)


@app.route('/')
def home_page():
    now = datetime.datetime.now()
    return render_template('home.html', current_time=now.ctime())

#test page to obtain some design ideas
@app.route('/timeline')
def timeline():
    now =datetime.datetime.now()
    return render_template('timeline.html', current_time=now.ctime())    

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/profile')
def profile():
    return render_template('profile.html')


@app.route('/notification')
def notification():
    context = []
    context.append("https://scontent-cdg2-1.cdninstagram.com/t51.2885-19/s150x150/12530676_203139496730851_641566517_a.jpg")
    context.append("http://www.drawingnow.com/file/videos/image/how-to-sketch-short-anime-female-hair.jpg")
    image_list = {
                  'image': context,
                                    }
    return render_template('notification.html', image = image_list)
	
if __name__ == '__main__':
    VCAP_APP_PORT = os.getenv('VCAP_APP_PORT')
    if VCAP_APP_PORT is not None:
        port, debug = int(VCAP_APP_PORT), False
    else:
        port, debug = 5000, True
    app.run(host='0.0.0.0', port=port, debug=debug)
