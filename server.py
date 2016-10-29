import datetime
import os
import psycopg2

from flask import Flask
from flask import render_template

try:
    #Get database information from environment
    _database = os.environ.get('psql_uri')
    _host = os.environ.get('psql_host')
    _user = os.environ.get('psql_user')
    _dbname = os.environ.get('psql_dbname')
    _password = os.environ.get('psql_password')
    #Connection for database
    conn = psycopg2.connect(database = _database,
    host = _host,
    user= _user,
    dbname= _dbname,
    password= _password)
except expression as identifier:
    raise "database error"


## execute image table query
#cmd = """"""

#_crs=conn.cursor()
#_crs.execute(cmd)
#conn.commit()

app = Flask(__name__)


@app.route('/')
def home_page():
    ##now = datetime.datetime.now()
    
    ##crs=conn.cursor()
    ##crs.execute("insert into images (user_id, path, time, text) values (1, 'path', now(), 'hello world')")
    ##conn.commit()

    ##crs.execute("select * from images")
    ##data = crs.fetchall()
    result = getScriptFileAsString()
    return render_template('home.html', current_time=result)

@app.route('/activity')
def activity():
    return render_template('activity.html')

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

@app.route('/upload')
def upload():
    return render_template('upload.html')


@app.route('/notification')
def notification():
    context = []
    context.append("https://scontent-cdg2-1.cdninstagram.com/t51.2885-19/s150x150/12530676_203139496730851_641566517_a.jpg")
    context.append("http://www.drawingnow.com/file/videos/image/how-to-sketch-short-anime-female-hair.jpg")
    image_list = {
                  'image': context,
                                    }
    return render_template('notification.html', image = image_list)
    
@app.route('/createDatabase')
def createDatabase():
    scripts = getScriptFileAsString()
    
    crs = conn.cursor()
    print(scripts)
    crs.executemany(scripts)
    result = conn.commit()

    return render_template('message.html', message = "Script is commited, the result is " + result)

#Read script.sql file as a single string
def getScriptFileAsString():

    #open script.sql file
    with open('script.sql') as f:
        #Read all lines
        content = f.readlines()
    #Clear the whitespaces
    for i in range(len(content)):
        content[i] = content[i].strip()

    #Merge all lines as one string
    result = ' '.join(content)

    return result

if __name__ == '__main__':
    VCAP_APP_PORT = os.getenv('VCAP_APP_PORT')
    if VCAP_APP_PORT is not None:
        port, debug = int(VCAP_APP_PORT), False
    else:
        port, debug = 5000, True
    app.run(host='0.0.0.0', port=port, debug=debug)

