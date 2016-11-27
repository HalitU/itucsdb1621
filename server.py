import datetime
import os
import psycopg2

from images import images_app
from notifications import notific_app
from register import RegisterForm
from register import register_app
from comments import comment_app
from directmessages import dmessage_app
from reports import reports_app
from flask import Flask, render_template, request


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = '/static/uploads'
app.register_blueprint(images_app)
app.register_blueprint(register_app)
app.secret_key = 'kiymetlimiss'
app.register_blueprint(comment_app) ## added comment bluprint
app.register_blueprint(notific_app)
app.register_blueprint(dmessage_app)
app.register_blueprint(reports_app)
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
    images = []
    with psycopg2.connect(app.config['dsn']) as conn:
        crs=conn.cursor()
        crs.execute("select * from images order by time desc")
        data = crs.fetchall()
        
        for img in data:
            #get all locations in one string that the image have
            crs.execute("select string_agg(locations.name, ',') from image_locations inner join locations on locations.id = image_locations.location_id where image_id = %s group by image_id", ([img[0]]))
            locs = crs.fetchone()

            if locs:

                marks = locs[0].split(',')
                for i in range(len(marks)):
                    marks[i] = '<a href="/location/{}">{}</a>'.format(marks[i], marks[i])
                
                locs = ','.join(marks)
                img = img + (locs,) #add new value to tuple
                images.append(img)
            else:
                images.append(img)

        ## get all comment need to change this sql statement later
        crs.execute("select * from comments order by time desc")
        ## group by then 2ds array
        comments = crs.fetchall()

    now =datetime.datetime.now()
    ## pass values
    return render_template('home.html', current_time=now.ctime(), list = images, images_app = images_app, comment_app = comment_app,comment_list=comments)

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

@app.route('/signup', methods = ['GET', 'POST'])
def signup():
    form = RegisterForm()
    if request.method == 'POST':
        return 'Registered.'

    elif request.method == 'GET':
        return render_template('signup.html', form=form,current_app=app)

@app.route('/dmessage')
def dmessage():
    with psycopg2.connect(app.config['dsn']) as conn:
        crs=conn.cursor()
        crs.execute("select * from directmessages order by time desc")
        dmessages = crs.fetchall()

    now =datetime.datetime.now()

    return render_template('dmessage.html', current_time=now.ctime(), dmessage_app = dmessage_app, dmessage_list=dmessages)

@app.route('/profile')
def profile():

    with psycopg2.connect(app.config['dsn']) as conn:
        crs = conn.cursor()
        crs.execute("select * from users order by username desc")
        usernames = crs.fetchall()
    return render_template('profile.html',usernames= usernames,register_app=register_app)

@app.route('/remove')
def remove():
    return render_template("remove.html",register_app=register_app)

@app.route('/update')
def update():
    return render_template("update.html",register_app=register_app)

@app.route('/notification')
def notification():
    with psycopg2.connect(app.config['dsn']) as conn:
        crs=conn.cursor()
        crs.execute("select * from notifications")
        data = crs.fetchall()

    return render_template('notification.html', image = data, notific_app = notific_app)

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

    return render_template('message.html', message = "Script is committed, the result is ")

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