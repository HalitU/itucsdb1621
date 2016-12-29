.. raw:: html

	<style> .danger{color:red} </style>

.. sectnum::

Parts Implemented by Alim Özdemir
=================================

You can find all informations about images, locations and filters here.

General Database Design
-----------------------

ER DIAGRAM
^^^^^^^^^^^^^^^
.. figure:: member3er.png


Images
------

Table
^^^^^^^^^^^^^^^

.. code-block:: sql

    CREATE TABLE IF NOT EXISTS images(
        image_id serial primary key,
        user_id int REFERENCES users(ID) ON DELETE CASCADE,
        path text ,
        time date ,
        text text
    );

The table above has critical fields that effects the whole system. Image_id is primary key and forgein key for other associated tables. A user could have many images. Therefore the table has one to many relationship with user_id.
Path field is the absolute url of uploaded image. Text field is description of that image.

Associated tables

.. code-block:: sql

    CREATE TABLE IF NOT EXISTS user_likes(
        user_id int REFERENCES users (ID) ON DELETE CASCADE,
        image_id int REFERENCES images (image_id) ON DELETE CASCADE,
        time date,
        primary key(image_id, user_id)
    );

    CREATE TABLE IF NOT EXISTS user_block(
        user_id int REFERENCES users (ID) ON DELETE CASCADE,
        blocked_id int REFERENCES users (ID) ON DELETE CASCADE,
        time date,
        primary key(user_id, blocked_id)
    );

The tables above are associated tables between users and images. 

Locations
---------

Table
^^^^^^^^^^^^^^^
.. code-block:: sql

    CREATE TABLE IF NOT EXISTS locations(
        Id serial primary key,
        name text,
        latitude numeric,
        longitude numeric,
        formatted_address text,
        rating real
    );
    CREATE TABLE IF NOT EXISTS image_locations(
        image_id int REFERENCES images (image_id) ON DELETE CASCADE,
        location_id int REFERENCES locations (Id) ON DELETE CASCADE,
        order_val int DEFAULT 0,
        primary key (image_id, location_id)
    );

Locations table represents of the geographic information of taken image. Sending text field to googlemaps REST API returns the fields latitude, longitude, formatted_address. 
Also, there exists many to many relationship between images and locations. (image_locations is the pivot table)

Filters
-------

Table
^^^^^^^^^^^^^^^

.. code-block:: sql

    CREATE TABLE IF NOT EXISTS filter(
        id serial primary key,
        name text,
        user_id int REFERENCES users (ID) ON DELETE CASCADE,
        Contrast int,
        Brightness int,
        Sharpness int,
        Blur int,
        UnsharpMask int
    );
    CREATE TABLE IF NOT EXISTS image_filters(
        filter_id int REFERENCES filter(id) ON DELETE RESTRICT,
        image_id int REFERENCES images(image_id) ON DELETE CASCADE
    );

The filter table stores information about user's custom data with pillow package of python.
A user could have many filters. And, there exists many to many relationship between images and filters. (image_filters is the pivot table)


Implementation using Flask on Python
------------------------------------

Controllers
^^^^^^^^^^^^^^^

Inserting of Image & Location & Filter

.. code-block:: python

    @images_app.route('/upload', methods = ['POST'])
    def upload_post():
        if not session.get('user_id'):
            return redirect(url_for('home_page'))

        comment = request.form['comment']
        location = request.form['location']
        upload_file = request.files['image']
        filters = request.form['filters']
        contrast = request.form['contrast']
        brightness = request.form['brightness']
        sharpness = request.form['sharpness']
        blur = request.form['blur']
        unsharpmask = request.form['unsharpmask']
        session_user_id = session['user_id']
        if upload_file:
            upload_file.save(os.path.join('static/uploads', upload_file.filename))
        else:
            return render_template('message.html', message = "Please select an image..")

        img = Image.open(os.path.join('static/uploads', upload_file.filename))
        
        needToSave = 0
        if blur != "0":
            img = img.filter(ImageFilter.GaussianBlur(float(blur)))
            needToSave = 1
        
        if unsharpmask != "0":
            img = img.filter(ImageFilter.UnsharpMask(float(unsharpmask)))
            needToSave = 1
        
        if sharpness != "0" :
            enhancer = ImageEnhance.Sharpness(img)
            img = enhancer.enhance(float(sharpness))
            needToSave = 1

        if contrast != "0" :
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(float(contrast))
            needToSave = 1

        if brightness != "0" :
            enhancer = ImageEnhance.Brightness(img)
            img = enhancer.enhance(float(brightness))
            needToSave = 1

        if needToSave == 1:
            img.save(os.path.join('static/uploads', upload_file.filename))

        print(filters)
        gmaps = googlemaps.Client(key='AIzaSyDurbt3tU9F8lDMqyHAnXVjCPphapNu0FM')
        with psycopg2.connect(current_app.config['dsn']) as conn:
            crs=conn.cursor()

            crs.execute("insert into images (user_id, path, time, text) values (%s,%s, now(), %s) RETURNING image_id", (session_user_id, upload_file.filename, comment))
            image_id = crs.fetchone()[0] #Get image id
            #filter part
            if filters == "0":
                crs.execute('insert into filter (name, user_id, contrast, Brightness, Sharpness, Blur, UnsharpMask) values (%s, %s, %s, %s, %s, %s, %s) RETURNING id',  ("Saved Settings", session_user_id,contrast, brightness, sharpness, blur, unsharpmask))
                filter_id = crs.fetchone()[0]
                crs.execute('insert into image_filters (image_id, filter_id) values (%s, %s)', (image_id, filter_id))
                conn.commit()
            else:
                crs.execute('update filter set contrast = %s, brightness = %s, sharpness = %s, blur = %s, unsharpmask = %s where id = %s and user_id = %s', (contrast, brightness, sharpness, blur, unsharpmask, filters, session_user_id))
                filter_id = filters
                crs.execute('insert into image_filters (image_id, filter_id) values (%s, %s)', (image_id, filter_id))
                conn.commit()
            if location:
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
            crs.execute("select photo_path, username from users where Id !=%s",(session['user_id'],))
            data = crs.fetchone()
            crs.execute("insert into notifications(user_id, notifier_id, notifier_name, icon, details, read_status, follow_status) values (%s, %s, %s, %s, %s, %s, %s)", (session['user_id'], session['user_id'], data[1] ,data[0], comment , 'FALSE', 'TRUE'))
            data = conn.commit()

        return render_template('message.html', message = "Uploaded..")


This action is responsible for
    #processing the image using `pillow`,
        
        #using user's existing filters
        #creating new filter data 
    
    #getting geographic data from googlemaps REST API,
    #uploading the image,
    #storing its data to the database
    #notifying the user/users about the image

The user selects the image that should be filtered and uploaded to system along with the informations such as description about the image, location of the image,
desired filter informations for `pillow` library to process, and then uploads the image.
The action checks about if user is logged in, and if the file input isn't empty. Applies image processing via `pillow` library using submitted filter data. Gets geographic data sending a query to googlemaps API via location input.

.. code-block:: python

    @images_app.route('/image_delete/<id>')
    def image_delete(id):
        #id = request.args.get('id')
        with psycopg2.connect(current_app.config['dsn']) as conn:           
            crs=conn.cursor()
            crs.execute("delete from images where image_id = %s", (id))
            data = conn.commit()
        
        return render_template('message.html', message = "Image deleted..")

This action deletes the image and its associated relations that are cascade.

.. code-block:: python

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

This JSON action updates the text field of the image.

.. code-block:: python

    @images_app.route('/image_like', methods = ['POST'])
    def image_like():
        if not session.get('user_id'):
            return redirect(url_for('home_page'))

        id = request.form['id']
        user_id = session['user_id']

        with psycopg2.connect(current_app.config['dsn']) as conn:           
            crs=conn.cursor()
            crs.execute("select * from user_likes where user_id = %s and image_id = %s", (user_id, id))
            exist = crs.fetchone()
            if exist:
                return jsonify(-1) #already liked.
            else:
                crs.execute("insert into user_likes (user_id, image_id, time) values (%s, %s, now())", (user_id, id))
                data = conn.commit()
        return jsonify(1)

This JSON action inserts a user like to the user_like table.

.. code-block:: python

    @images_app.route('/image_unlike', methods = ['POST'])
    def image_unlike():
        if not session.get('user_id'):
            return redirect(url_for('home_page'))
        id = request.form['id']    
        user_id = session['user_id'] 

        with psycopg2.connect(current_app.config['dsn']) as conn:           
            crs=conn.cursor()
            crs.execute("select * from user_likes where user_id = %s and image_id = %s", (user_id, id))
            exist = crs.fetchone()
            if exist:
                crs.execute("delete from user_likes where user_id = %s and image_id = %s", (user_id, id))
                data = conn.commit()
            else:
                return jsonify(-1)
        return jsonify(1)

This JSON action deletes a user like from the user_like table.

.. code-block:: python

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

This action contains all operations ( such as updating, inserting, deleting ) about the location using `tagsinput` library.

.. code-block:: python

    @images_app.route("/locations")
    def locations():
        if not session.get('user_id'):
            return redirect(url_for('home_page'))
        with psycopg2.connect(current_app.config['dsn']) as conn:           
            crs=conn.cursor()
            crs.execute('select * from locations order by rating desc')
            data = crs.fetchall()
        return render_template('locations.html', list = data)

This action lists all locations that persisted on the database.

.. code-block:: python

    @images_app.route('/remove_location/<id>')
    def remove_location(id):

        with psycopg2.connect(current_app.config['dsn']) as conn:           
            crs=conn.cursor()
            crs.execute('delete from locations where Id = %s', (id))
            conn.commit()

        return render_template('message.html', message = "Location has been removed from database")

This action deletes given location with all of its associated data from the database.

.. code-block:: python

    @images_app.route('/location/<name>')
    def location(name):
        with psycopg2.connect(current_app.config['dsn']) as conn:           
            crs=conn.cursor()
            crs.execute('select * from locations where name = %s', (name,))
            data = crs.fetchone()
            if data:
                crs.execute('select count(*) from image_locations where location_id = %s', ([data[0]]))
                count = crs.fetchone()[0]
            else:
                return render_template('message.html', message="No location with '{}' name".format(name))
        return render_template('location.html', data = data, count = count)

This action used to show detailed view of the given location.

.. code-block:: python

    @filters_app.route('/filter/index')
    def index():
        if not session.get('user_id'):
            return redirect(url_for('home_page'))

        session_user_id = session['user_id']

        with psycopg2.connect(current_app.config['dsn']) as conn:           
            crs = conn.cursor()
            crs.execute("select id,name from filter where user_id = %s", (session_user_id,))
            data = crs.fetchall()

        return render_template('filter_index.html', list = data)

This action lists the saved filters of logged in user.

.. code-block:: python

    @filters_app.route('/filter/fetch', methods = ['POST'])
    def fetch():
        if not session.get('user_id'):
            return redirect(url_for('home_page'))

        id = request.form['id']
        session_user_id = session['user_id']

        with psycopg2.connect(current_app.config['dsn']) as conn:           
            crs = conn.cursor()
            crs.execute("select * from filter where user_id = %s and id = %s", (session_user_id,id))
            data = crs.fetchone()

        return jsonify(data)

This JSON action gets a single existing filter.

.. code-block:: python

    @filters_app.route('/filter/delete', methods = ['POST'])
    def delete():
        if not session.get('user_id'):
            return redirect(url_for('home_page'))

        id = request.form['id']
        session_user_id = session['user_id']
        if id == "1":
            return redirect(url_for('home_page'))

        with psycopg2.connect(current_app.config['dsn']) as conn:           
            crs = conn.cursor()
            crs.execute("select * from filter where user_id = %s and id = %s", (session_user_id,id))
            data = crs.fetchone()
            if data:
                crs.execute("delete from filter where user_id = %s and id = %s", (session_user_id, id))
                conn.commit()
            else:
                return render_template('message.html', message = "No record has found.")

        return render_template('message.html', message = "filter deleted")

This action deletes the saved filter from the database.

.. code-block:: python

    @filters_app.route('/filter/update', methods = ['POST'])
    def update():
        if not session.get('user_id'):
            return jsonify(None)

        id = request.form['id']
        
        contrast = request.form['contrast']
        brightness = request.form['brightness']
        sharpness = request.form['sharpness']
        blur = request.form['blur']
        unsharpmask = request.form['unsharpmask']

        session_user_id = session['user_id']

        with psycopg2.connect(current_app.config['dsn']) as conn:           
            crs = conn.cursor()
            crs.execute("select * from filter where user_id = %s and id = %s", (session_user_id,id))
            data = crs.fetchone()
            #update
            if data:
                crs.execute('update filter set contrast = %s, brightness = %s, sharpness = %s, blur = %s, unsharpmask = %s where id = %s and user_id = %s', (contrast, brightness, sharpness, blur, unsharpmask, id, session_user_id))
                conn.commit()
                
        return jsonify(True)

This JSON action updates the existing filter data.