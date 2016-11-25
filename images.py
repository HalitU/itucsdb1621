import os
import psycopg2
import googlemaps
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

    gmaps = googlemaps.Client(key='AIzaSyDurbt3tU9F8lDMqyHAnXVjCPphapNu0FM')
    with psycopg2.connect(current_app.config['dsn']) as conn:           
            crs=conn.cursor()
            crs.execute("insert into images (user_id, path, time, text) values (%s, %s, now(), %s) RETURNING image_id", (2, upload_file.filename, comment))
            image_id = crs.fetchone()[0] #Get image id
            locs = location.split(',')
            order = 0
            #location check
            for loc in locs:
                #print(loc)
                crs.execute("select * from locations where name = %s", (loc,))
                loc_data = crs.fetchone()
                loc_id = 0
                #get location id with insert or select
                if loc_data:
                    crs.execute('update locations set rating = rating + 1 where Id=%s', ([loc_data[0]]))
                    loc_id = loc_data[0]
                else:
                    gcode = gmaps.geocode(loc)
                    formatted = gcode[0]['formatted_address']
                    location = gcode[0]['geometry']['location']
                    lng = location['lng']
                    lat = location['lat']
                    crs.execute('insert into locations (name, latitude, longitude, formatted_address, rating) values (%s, %s, %s, %s, %s) RETURNING Id', (loc, lat, lng, formatted, 1))
                    loc_id = crs.fetchone()[0] #Get last insertion id
                
                #add it to image_locations relation table
                crs.execute('insert into image_locations (image_id, location_id, order_val) values (%s, %s, %s)', (image_id, loc_id, order))
                order = order + 1

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


@images_app.route('/update_delete_loc/<id>')
def update_delete_loc(id):
    with psycopg2.connect(current_app.config['dsn']) as conn:           
        crs=conn.cursor()
        crs.execute("select string_agg(locations.name, ', ') from image_locations inner join locations on locations.id = image_locations.location_id where image_id = %s group by image_id", (id))
        locations = crs.fetchone()
    
    if locations:
        data = locations[0]
    else:
        data = ""
    return render_template('update_loc.html', image_id = id, locs = data)

@images_app.route('/update_delete_loc_save', methods = ['POST'])
def update_delete_loc_save():
    id = request.form['id']
    locs = request.form['locs']
    locations = locs.split(',')
    
    gmaps = googlemaps.Client(key='AIzaSyDurbt3tU9F8lDMqyHAnXVjCPphapNu0FM')
    #collect updated or inserted ids
    collect = []

    with psycopg2.connect(current_app.config['dsn']) as conn:           
        crs=conn.cursor()
        for loc in locations:
            crs.execute("select * from locations where name = %s", (loc,))
            loc_data = crs.fetchone()
            if loc_data:
                crs.execute('update locations set rating = rating + 1 where Id = %s', ([loc_data[0]]))
                collect.append(loc_data[0])
            else:
                gcode = gmaps.geocode(loc)
                formatted = gcode[0]['formatted_address']
                location = gcode[0]['geometry']['location']
                lng = location['lng']
                lat = location['lat']
                crs.execute('insert into locations (name, latitude, longitude, formatted_address, rating) values (%s, %s, %s, %s, %s) RETURNING Id', (loc, lat, lng, formatted, 1))
                loc_id = crs.fetchone()[0] #Get last insertion id
                collect.append(loc_id)

        crs.execute('select location_id from image_locations where image_id = %s', (id))
        currentLocs = crs.fetchall()
        
        #tuple array to int array
        currentLocsInt = []
        for cur in currentLocs:
            currentLocsInt.append(cur[0])

        finded = []
        for cur in collect:
            if cur not in currentLocsInt:
                crs.execute('insert into image_locations (image_id, location_id) values (%s, %s)', (id, cur))
                finded.append(cur)
        #Delete from database that not match
        for cur in currentLocsInt:
            if cur not in collect:
                crs.execute('delete from image_locations where image_id = %s and location_id = %s', (id, cur))
        
        #get all locations and update order
        crs.execute('select location_id from image_locations where image_id = %s', (id))
        updateLocs = crs.fetchall()
        order = 0
        for u in updateLocs:
            crs.execute('update image_locations set order_val = %s where image_id = %s', (order, id))
            order = order + 1
        conn.commit()
    return render_template('message.html', message = "Locations updated..")

@images_app.route("/locations")
def locations():
    
    with psycopg2.connect(current_app.config['dsn']) as conn:           
        crs=conn.cursor()
        crs.execute('select * from locations order by rating desc')
        data = crs.fetchall()
    return render_template('locations.html', list = data)

@images_app.route('/remove_location/<id>')
def remove_location(id):

    with psycopg2.connect(current_app.config['dsn']) as conn:           
        crs=conn.cursor()
        crs.execute('delete from locations where Id = %s', (id))
        conn.commit()

    return render_template('message.html', message = "Location has been removed from database")

@images_app.route('/geoloc')
def geoloc():
    gmaps = googlemaps.Client(key='AIzaSyDurbt3tU9F8lDMqyHAnXVjCPphapNu0FM')
    geocode = gmaps.geocode('Beylikdüzü istanbul')
    location = geocode[0]['geometry']['location']
    lng = location['lng']
    lat = location['lat']
    return render_template('message.html', message = geocode[0]['formatted_address'])

@images_app.route('/location/<name>')
def location(name):
    with psycopg2.connect(current_app.config['dsn']) as conn:           
        crs=conn.cursor()
        crs.execute('select * from locations where name = %s', (name))
        data = crs.fetchone()
    print(data)
    return render_template('location.html', data = data)