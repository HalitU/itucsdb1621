import os
import psycopg2
from flask import Flask
from flask import render_template, request
from flask import Blueprint, current_app

#declaring sub app with blueprint
images_app = Blueprint('images_app', __name__)

@images_app.route('/upload')
def upload():
    with psycopg2.connect(current_app.config['dsn']) as conn:           
            crs = conn.cursor()
            crs.execute("select * from images")
            data = crs.fetchall()
            print(data)

    return render_template('upload.html')

@images_app.route('/upload', methods = ['POST'])
def upload_post():

    comment = request.form['comment']
    upload_file = request.files['image']
    upload_file.save(os.path.join('static/uploads', upload_file.filename))

    with psycopg2.connect(current_app.config['dsn']) as conn:           
            crs=conn.cursor()
            crs.execute("insert into images (user_id, path, time, text) values (%s, %s, now(), %s)", (2, upload_file.filename, comment))
            data = conn.commit()

    return render_template('message.html', message = "Uploaded..")

@images_app.route('/image_delete/<id>')
def image_delete(id):
    #id = request.args.get('id')
    with psycopg2.connect(current_app.config['dsn']) as conn:           
            crs=conn.cursor()
            crs.execute("delete from images where image_id = %s", (id))
            data = conn.commit()
    
    return render_template('message.html', message = "Image deleted..")