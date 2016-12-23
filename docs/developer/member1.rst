.. raw:: html

	<style> .danger{color:red} </style>

.. sectnum::
Parts Implemented by Sıddık Açıl
================================

Comments, content reporting, and image tagging is implemented by me.

General Database Design
-----------------------

.. figure:: member1er.png

	ENTITY-RELATIONSHIP DIAGRAM OF MY PART

Comments
--------

Database Design
^^^^^^^^^^^^^^^

.. code-block:: sql

	CREATE TABLE IF NOT EXISTS comments (
		comment_id serial primary key,
		user_id int REFERENCES users(ID) ON DELETE CASCADE,
		image_id int REFERENCES images(image_id) ON DELETE CASCADE,
		time date,
		comment text
	);


Comments table has a serial primary key and two foreign keys, one to users table, other to images table. Users and images both has 1-n relation with comments, meaning that a user can make many comments and a images may have many comments made on.


Controller Code
^^^^^^^^^^^^^^^
.. code-block:: python
	
	from flask import Flask
	from flask import render_template, request, session
	from flask import Blueprint, current_app

	#declaring sub app with blueprint
	comment_app = Blueprint('comment_app', __name__)

As with other components this one uses Flask's Blueprint interface to modulate project into seperate files and therefore isolates workspace, improves readability and most importantly eliminates conflicts.

.. code-block:: python

	@comment_app.route('/comment/<image_id>',methods=["POST"])
	def comment(image_id):
		print("Hey")
		## insert
		comment = request.form['comment']
		with psycopg2.connect(current_app.config['dsn']) as conn:
		        crs=conn.cursor()
		        crs.execute("insert into comments (user_id, image_id, time, comment) values (%s, %s, now(), %s)", (session.get("user_id"), image_id, comment))
		        data = conn.commit()

		return render_template('message.html', message = "Successfully commented..")


This controller gets data from specific forms in image divs in home.html. Thus image_id parameter corresponds to the image_id parameter of the form action. Comment text is acquired via request api which parses request parameters and creates a dictionary named form. 
	* A disposable connection to database server is created via 'with' command which gets configuration from main application(current_app) settings.  
	* Create a cursor.
	* Execute an SQL insertion.
	* Commit the changes and save the result of query.

Function then returns a rendered template messages.html which is used to 'flash' results of actions throughout the entire project.

.. code-block:: python

	@comment_app.route('/comment_delete/<id>')
	def comment_delete(id):
		## delete
		#id = request.args.get('id')
		with psycopg2.connect(current_app.config['dsn']) as conn:
		        crs=conn.cursor()
		        crs.execute("delete from comments where comment_id = %s", (id))
		        data = conn.commit()

		return render_template('message.html', message = "Comment deleted..")


When a user presses delete icon near a comment of his/her own it is routed to this route which gets id of the comment to be deleted from routing argument '<id>'. Then the function connects to database driver, instantiates a cursor, executes delete SQL query with id and commits to the database. Return a "message.html" template denoting that the message has been deleted.

.. code-block:: python

	@comment_app.route("/comment_update/<id>",methods=["POST"])
	def comment_update(id):
		new_comment = request.form["new_comment"]
		with psycopg2.connect(current_app.config["dsn"]) as conn:
		    crs = conn.cursor()
		    crs.execute('update comments set time=now(),comment=%s where comment_id=%s ',(new_comment,id))
		    conn.commit()

	return render_template("message.html",message="You have changed your comment successfully")

The same procedure for delete hold true for update except that it is reached by update button in home.html. SQL query seeks the comment to be updated and changes its time and content. And returns the message.html template which flashes a success message.


.. note:: A non-existing id is not handled in update and delete operations, since user input can not be a non-existent id.
.. role:: red
.. DANGER:: However by typing comment_delete/comment_update manually, a user may try to delete or update a non-existent entry in which server stops execution halfway informing user.

.. role:: red
.. DANGER:: This component belongs to the early stages of the project so no session data is checked. Therefore anyone can delete/update any comment by typing comment_delete/<id> or comment_update/<id>. However, this behavior does not apply to the user interface as no delete button appears to user for comments which is not written by him/her.


Content Reports
---------------

Database Design
^^^^^^^^^^^^^^^

.. code-block:: sql

	CREATE TABLE IF NOT EXISTS content_reports(
	    report_id serial primary key,
	    user_id INT REFERENCES users (ID) ON DELETE CASCADE,
	    image_id INT REFERENCES images (image_id) ON DELETE CASCADE,
	    report_comment text,
	    status text,
	    time date
	);


Controller Code
^^^^^^^^^^^^^^^

Image Tags
----------

Database Design
^^^^^^^^^^^^^^^

.. code-block:: sql

	CREATE TABLE IF NOT EXISTS tags(
	    tagger_id INT REFERENCES users (ID) ON DELETE CASCADE,
	    tagged_id INT REFERENCES users(ID) ON DELETE CASCADE,
	    photo_id INT REFERENCES images(image_id) ON DELETE CASCADE,
	    time date,
	    x INT,
	    y INT,
	    primary key (tagger_id,tagged_id,photo_id)
	);

Controller Code
^^^^^^^^^^^^^^^



