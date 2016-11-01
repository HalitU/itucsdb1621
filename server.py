import datetime
import os
import psycopg2
from images import images_app

from flask import Flask
from flask import render_template


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = '/static/uploads'
app.register_blueprint(images_app)

class DB_Error(Exception):
    pass
try:
    #Get database information from environment
    _database = os.environ.get('psql_uri')
    _host = os.environ.get('psql_host')
    _user = os.environ.get('psql_user')
    _dbname = os.environ.get('psql_dbname')
    _password = os.environ.get('psql_password')

    _port = 5432
    dsn = """user='{}' password='{}' host='{}' port={}
        dbname='{}'""".format(_user, _password, _host, _port, _dbname) 
    app.config['dsn'] = dsn
    #Connection for database

except DB_Error:
    raise "database error"

@app.route('/')
def home_page():

    with psycopg2.connect(app.config['dsn']) as conn:
        crs=conn.cursor()
        crs.execute("select * from images order by time desc")
        data = crs.fetchall()
    
    now =datetime.datetime.now()
    return render_template('home.html', current_time=now.ctime(), list = data, images_app = images_app)

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
    queries = scripts.split(';')
    
    with psycopg2.connect(app.config['dsn']) as conn:
        for i in queries:
            t = i.strip()
            if t:
                print(t)
                crs = conn.cursor()    
                crs.execute(t)
            conn.commit()

    return render_template('message.html', message = "Script is commited, the result is ")

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

