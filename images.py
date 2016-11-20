import os
import psycopg2
from flask import Flask
from flask import render_template, request, jsonify
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
    location = request.form['location']
    upload_file = request.files['image']
    if upload_file:
        upload_file.save(os.path.join('static/uploads', upload_file.filename))
    else:
        return render_template('message.html', message = "Please select an image..")
    with psycopg2.connect(current_app.config['dsn']) as conn:           
            crs=conn.cursor()
            crs.execute("insert into images (user_id, path, time, text) values (%s, %s, now(), %s) RETURNING image_id", (2, upload_file.filename, comment))
            image_id = crs.fetchone()[0] #Get image id
            locs = location.split(',')

            #location check
            for loc in locs:
                #print(loc)
                crs.execute("select * from locations where name = %s", (loc,))
                loc_data = crs.fetchone()
                loc_id = 0
                #get location id with insert or select
                if loc_data:
                    loc_id = loc_data[0]
                else:
                    crs.execute('insert into locations (name, rating) values (%s, %s) RETURNING Id', (loc_data, 1))
                    loc_id = crs.fetchone()[0] #Get last insertion id
                print(loc_id)
                #add it to image_locations relation table
                crs.execute('insert into image_locations (image_id, location_id) values (%s, %s)', (image_id, loc_id))

            #notification insertion will use the logged user's information after the respective functionality is added - Halit
            crs.execute("insert into notifications(user_id, notifier_id, notifier_name, icon, details, read_status, follow_status) values (%s, %s, %s, %s, %s, %s, %s)", (1, 2, 'some_company' ,'notific_sample.jpg', 'Thanks for all followers!' , 'FALSE', 'TRUE'))
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


@images_app.route('/image_update', methods = ['POST'])
def image_update():
    #inline editable plugin gives pk and value
    id = request.form['pk']
    newText = request.form['value']
    data = ""
    with psycopg2.connect(current_app.config['dsn']) as conn:           
            crs=conn.cursor()
            crs.execute("update images set text=%s where image_id = %s", (newText, id))
            data = conn.commit()
            return jsonify(data)

    return jsonify(0)

@images_app.route('/image_like', methods = ['POST'])
def image_like():

    

    return jsonify(0)