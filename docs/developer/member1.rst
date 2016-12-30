.. raw:: html

	<style> .danger{color:red} </style>

.. sectnum::
Parts Implemented by Sıddık Açıl
================================

.. role:: sql(code)
	:language: sql
.. role:: python(code)
	:language: python

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

.. code-block:: python

	@app.route('/')
	def home_page():
		### .....
 		comments= []
		for img in data:
		    crs.execute("select comment_id, user_id,image_id,time,comment,username from comments join users on comments.user_id = users.ID where image_id=%s",(img[0],))
		    conn.commit()
		    comments.append(crs.fetchall())
		### ......
	return render_template('home.html', current_time=now.ctime(), list = images, images_app = images_app, comment_app = comment_app,comment_list=comments, likes = userlikes,tags_app=tags_app,tags=tags)

Inside of home page root comments need to be passed in template in a manner that every image element has a comments list associated with itself(So it is basically a 2D-List of comments). This is achieved by joining :sql:`users` and :sql:`comments` table and filtering the query on :python:`image_id` for each element in images to be shown on home page.

.. note:: It would be better not to execute the query for every element but to execute it once and map the result list to a 2D-List on photo_id.

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


Content report has 
	* a unique surrogate key:  :sql:`report_id`
	* a reference to the user who has issued the report :sql:`user_id`
	* a reference to the image that has been reported :sql:`image_id`
	* a text on the report cause by the issuer :sql:`report_comment`
	* a status field whether if it is pending or accepted :sql:`status`
	* time of the report issue


Controller Code
^^^^^^^^^^^^^^^


.. code-block:: python

	from flask import render_template, request, jsonify
	from flask import Blueprint, current_app
	import psycopg2

	reports_app = Blueprint("reports_app",__name__)

As with other components this one uses Flask's Blueprint interface to modulate project into seperate files and therefore isolates workspace, improves readability and most importantly eliminates conflicts.

.. code-block:: python

	@reports_app.route('/initiate_report/<content_id>')
	def initiate_report(content_id):

	    with psycopg2.connect(current_app.config['dsn'])  as conn:
		crs = conn.cursor()
		crs.execute("select path from images where image_id=%s",(content_id))
		conn.commit()
		data = crs.fetchone()
	    return render_template("report.html",content_id=content_id,content=data)

The route :python:`initate_report/<content_id>` have an argument on which image is reported, and uses this object to select corresponding image via a disposable connection to application database. This function returns a template which shows up the aforementioned image with a form inquiring the cause of report and sends data to :python:`report_content` route, the next element on the Content Reporting pipeline.

.. code-block:: python

	@reports_app.route('/report_content/<content_id>',methods=["POST"])
	def report_content(content_id):
	    report_text = request.form['report_text']
	    status ='pending'
	    with psycopg2.connect(current_app.config['dsn']) as conn:
		crs = conn.cursor()
		crs.execute("insert into content_reports (report_id,user_id, image_id, report_comment, status, time) values (DEFAULT,%s, %s, %s, %s, now())",(1,content_id,report_text,status))
		conn.commit()
	    return render_template("message.html",message="Content successfully reported.")

The next function in Content Report system gets the argument :python:`content_id` from the form on "Report" template page. 
	* :python:`report_text = request.form['report']` gets users' report on the content.
	* :python:`status ='pending` hold the initial status: pending

A connection is established to the database and and Insert query is dispatched to fill in content_reports page which is later used to view and process issues.

.. note:: :python:`user_id` being default is because of the website did not have session management when this feature has been added.

A quick fix on that line would be:

.. code-block:: python

	crs.execute("insert into content_reports (report_id,user_id, image_id, report_comment, status, time) values (DEFAULT,%s, %s, %s, %s, now())",(session.get("user_id"),content_id,report_text,status))


When viewing issues page an administrator(a feature which is not implemented) can go two ways with report, either accept or reject the deletion proposal.

.. code-block:: python

	@reports_app.route('/issue_approval/<content_id>',methods=["POST"])
	def issue_approval(content_id):
	    with psycopg2.connect(current_app.config['dsn']) as conn:
		crs = conn.cursor()
		crs.execute("delete from images where image_id = %s",(content_id)) 
		conn.commit()
	    return render_template("message.html",message="Content removed successfully.")

.. code-block:: python

	@reports_app.route('/issue_reject/<content_id>',methods=["POST"])
	def issue_reject(content_id):
	    with psycopg2.connect(current_app.config['dsn']) as conn:
		crs = conn.cursor()
		crs.execute("update content_reports set status='rejected' where image_id=%s",(content_id))
		conn.commit()
	    return render_template("message.html",message="Report rejected.")

If a deletion proposal is accepted, the form will go on to :python:`issue_approval/<content_id>` route to delete image with the :python:`content_id`. But, if a content report is rejected, its status will change from :sql:`pending` to :sql:`rejected`.


.. code-block:: python

	@app.route('/issues')
	def issues():
	    if session.get('logged_in')== None:
		return redirect(url_for("loginpage"))
	    with psycopg2.connect(app.config['dsn']) as conn:
		crs = conn.cursor()
		crs.execute("select (username,image_id,report_comment,status,time) from content_reports join users on content_reports.user_id= users.ID order by time")
		conn.commit()
		data = []
		ret = crs.fetchall()
		for tp in ret:
		    str = tp[0]
		    tmplist= []
		    for s in str.split(','):
		        tmplist.append(s)
		    data.append(tmplist)
		print(data)
	    return render_template("issues.html",data=data)

A join of :sql:`users` and :sql:`content_reports` are selected and passed into Issue template after a few formatting. Every element in result list which holds tuples is converted to string then split by delimiter "," and the result is a 2D-List. 

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

.. role:: sql(code)
	:language: sql

Image tags table consists of the following fields:
	* a reference to the tagger's id:  :sql:`tagger_id`
	* a reference to the id of the user who has been tagged on image :sql:`tagged_id`
	* a reference to the image that has been tagged :sql:`image_id`
	* time of tagging
	* x coordinate(percentage) of tag :sql:`x`
	* y coordinate(percentage) of tag :sql:`y`
	* a primary key consisting of  id of tagger, tagged and image :sql:`primary key (tagger_id,tagged_id,photo_id)`


Controller Code
^^^^^^^^^^^^^^^

.. code-block:: python

	import psycopg2
	from flask import Flask
	from flask import render_template, request
	from flask import Blueprint, current_app,session,redirect, url_for

	#declaring sub app with blueprint
	tags_app = Blueprint('tags_app', __name__)

As with other components this one uses Flask's Blueprint interface to modulate project into seperate files and therefore isolates workspace, improves readability and most importantly eliminates conflicts.

.. code-block:: python

	@tags_app.route('/add_tag/<photo_id>/', methods=["POST"])
	def add_tag(photo_id):
	    username = request.form["username"]
	    x = request.form["x"]
	    y = request.form["y"]
	    with psycopg2.connect(current_app.config['dsn']) as conn:
		crs = conn.cursor()
		crs.execute("select ID from users where username=%s",(username,))
		conn.commit()
		tagged_id = crs.fetchone()
		if tagged_id == None:
		    return render_template("message.html",message="User not found")
		## if null show and error message
		crs.execute("insert into tags (tagger_id,tagged_id,photo_id,time,x,y) values (%s,%s,%s,now(),%s,%s)",(session["user_id"],tagged_id,photo_id,x,y))
		conn.commit()
	    return render_template('message.html',message="Successfully added tag")

:python:``add_tag/<photo_id>` route gets a photo_id argument which holds the id of the image to be tagged. Following parameters are acquired from the form
	* :python:`username = request.form["username"]` holds the name of the user tagged.
	* :python:`x = request.form["x"]` holds the x coordinate that is clicked by tagger.
	* :python:`y = request.form["y"]` holds the y coordinate that is clicked by tagger.

On this controller two SQL queries are issued:
	1. An select query to get id from username. If no user is matched then controller returns a message template which flashes :python:`User not found`
	2. A query that populates tags table with id of tagger (from session), id of tagged (from previous query), id of image,x,y (from form variables).

.. code-block:: python

	@tags_app.route('/update_tag/<photo_id>/', methods=["POST"])
	def update_tag(photo_id):
	    newUsername = request.form["username"]
	    x = request.form["x"]
	    y = request.form["y"]
	    tagged_id=request.form["_id"]
	    with psycopg2.connect(current_app.config['dsn']) as conn:
		crs = conn.cursor()
		crs.execute("select ID from users where username=%s",(newUsername,))
		newId = crs.fetchone()
		if newId == None:
		    return render_template("message.html",message="User not found")
		print(tagged_id)

		## if null show and error message
		crs.execute("update tags set tagged_id=%s,time=now(),x=%s,y=%s where tagger_id=%s and tagged_id=%s and photo_id=%s  ",(newId[0],x,y,session["user_id"],tagged_id,photo_id))
		conn.commit()
	    return render_template('message.html',message="Successfully updated tag")

Update user controller works in the same fashion as :python:`add_tag` does.


:python:``update_tag/<photo_id>` route gets a photo_id argument which holds the id of the image to be tagged. Following parameters are acquired from the form
	* :python:`username = request.form["username"]` holds the name of the user tagged.
	* :python:`x = request.form["x"]` holds the x coordinate that is clicked by tagger.
	* :python:`y = request.form["y"]` holds the y coordinate that is clicked by tagger.

On this controller two SQL queries are issued:
	1. An select query to get id from username. If no user is matched then controller returns a message template which flashes :python:`User not found`
	2. A query that updates id of tagger,x,y of the row that matches on primary key fields.

.. code-block:: python

	@tags_app.route('/delete_tag/<photo_id>/', methods=["POST"])
	def delete_tag(photo_id,):
	    tagged_id=request.form["_id"]
	    with psycopg2.connect(current_app.config['dsn']) as conn:
		crs = conn.cursor()
		print(tagged_id)
		crs.execute("delete from tags where tagger_id=%s and tagged_id=%s and photo_id=%s  ",(session["user_id"],tagged_id,photo_id))
		conn.commit()
	    return render_template('message.html',message="Successfully deleted tag")

:python:`delete_tag/<photo_id>` gets id of the photo that user wants to delete a tag on. Since a photo may have many tags a way to distinguish between tags was put in use, :python:`tagged_id`. That way individual tags can be deleted. :sql:`tagged_id` field is gotten from a button when on clicked fills in hidden fields in form data with key :python:`_id`. 

.. code-block:: python

	@app.route('/')
	def home_page():
		tags=[]
       		for img in data:
			### .....
	   		crs.execute("select username,tagged_id,time,x,y from tags join users on users.ID = tags.tagger_id where photo_id=%s",(img[0],))
			conn.commit()
			tags.append(crs.fetchall())
			### .....
		return render_template('home.html', current_time=now.ctime(), list = images, images_app = images_app, comment_app = comment_app,comment_list=comments, likes = userlikes,tags_app=tags_app,tags=tags)

Inside of home page root tags need to be passed in template in a manner that every image element has a tags list associated with itself(So it is basically a 2D-List of tags). This is achieved by joining :sql:`users` and :sql:`tags` table and filtering the query on :python:`photo_id` for each element in images to be shown on home page.

.. note:: It would be better not to execute the query for every element but to execute it once and map the result list to a 2D-List on photo_id.

Users and User Follow
---------------------


Controller Code
^^^^^^^^^^^^^^^

I implemented this controller partially, so I left the part which was not written by me (except user block feature).

.. code-block:: python

	import psycopg2
	from flask import Flask
	from flask import render_template, request
	from flask import Blueprint, current_app,session,redirect, url_for

	#declaring sub app with blueprint
	users_app = Blueprint('users_app', __name__)

As with other components this one uses Flask's Blueprint interface to modulate project into seperate files and therefore isolates workspace, improves readability and most importantly eliminates conflicts.

.. code-block:: python

	@users_app.route('/search_user/',methods=['GET'])
	def search_user():
	    with psycopg2.connect(current_app.config['dsn']) as conn:
		username = request.args.get('username')
		if(username == ""):
		    username = " "
		print(type(username))
		crs = conn.cursor()
		crs.execute("select ID,username,photo_path from users where username like %s",(username,))
		print(username)
		conn.commit()
		result = crs.fetchall()
	    return render_template('search_results.html',result=result)

:python:`search_user` is implementation of basic exact match search feature on username field. The form uses get method ,since it does not do any modifications on database. If no argument is provided , username is changed so that it can list every user registered.

.. code-block:: python

	@users_app.route('/show_profile/<user_id>')
	def show_profile(user_id):
	    with psycopg2.connect(current_app.config['dsn']) as conn:
		crs = conn.cursor()
		crs.execute("select ID,username,photo_path,email from users where ID = %s",(user_id))
		conn.commit()
		result = crs.fetchone()
		crs.execute("select * from user_follow where follower_id=%s and  followed_id=%s",(session.get("user_id"),user_id))
		conn.commit()
		follow_query=crs.fetchone()
		is_following = False if follow_query == None else True
		is_self = False 
		if int(user_id) == session.get("user_id"):
		    is_self = True # can not follow oneself
		crs.execute("select path from images where user_id =%s",(user_id))
		conn.commit()
		list_photos = crs.fetchall()
	    return render_template('profile.html',result=result,is_following=is_following,is_self=is_self,list_photos=list_photos)

This controller return a rendered profile page. Since anyone can view any profile it should support viewing any profile which is why it takes a :python:`user_id` argument. On show profile section in home page user is simply routed to :python:`show_profile/<user_id>` when :python:`user_id` is :python:`session.get("user_id")`.

Queries executed:
	1. First query selects user information on given :sql:`user_id`
	2. Second query selects the information on :sql:`user_follow` table so that target profile page can be rendered according to follow/unfollow situation between current user and and the user profile he/she views. :python:`is_following`  variable holds this information. 
	3. Third query selects paths to photos which are uploaded by the user with :python:`user_id`

How is rendering modified:
	* :python:`is_following` variable change the rendering by changing between follow/unfollow buttons according to the current relation between current user and viewed user. If current user follows the viewed one than "Unfollow" button appears, otherwise a "Follow" button appears.
	* :python:`is_self` variable removes follow/unfollow buttons altogether since a user cannot unfollow himself/herself.

.. code-block:: python

	@users_app.route('/user_follow/<followed>')
	def user_follow(followed):
	     with psycopg2.connect(current_app.config['dsn']) as conn:
		crs = conn.cursor()
		crs.execute("insert into user_follow (follower_id,followed_id,time) values (%s,%s,now())",(session["user_id"],followed))
		conn.commit()
	     return render_template('message.html',message="Successfully followed")

This function allows current user to follow another user with id of :python:`followed`.

.. code-block:: python

	@users_app.route('/user_unfollow/<followed>')
	def user_unfollow(followed):
	    with psycopg2.connect(current_app.config['dsn']) as conn:
		crs = conn.cursor()
		crs.execute("delete from user_follow where follower_id=%s and followed_id=%s",(session["user_id"],followed))
		conn.commit()
	    return render_template('message.html',message="Successfully unfollowed")

This function allows current user to unfollow another user with id of :python:`followed`.
	
.. code-block:: python

	@users_app.route('/show_followers/<user_id>')
	def show_followers(user_id):
	    with psycopg2.connect(current_app.config['dsn']) as conn:
		crs = conn.cursor()
		crs.execute("select ID,username,photo_path from users where ID in (SELECT follower_id from user_follow where followed_id = %s)",(user_id,))
		conn.commit()
		ulist =crs.fetchall()
	    return render_template('user_list.html',ulist=ulist,user_id=user_id)

This function lists all of the followers of user with id of :python:`user_id`. Gets every user with if they have their id in the set which is return by SQL subquery which get :python:`follower_id` where :python:`followed_id` is :python:`user_id`.

.. code-block:: python

	@users_app.route('/show_followed/<user_id>')
	def show_followed(user_id):
	    with psycopg2.connect(current_app.config['dsn']) as conn:
		crs = conn.cursor()
		crs.execute("select ID,username,photo_path from users where ID in (SELECT followed_id from user_follow where follower_id = %s)",(user_id,))
		conn.commit()
		ulist =crs.fetchall()
	    return render_template('user_list.html',ulist=ulist,user_id=user_id)

This function lists all of the users followed by the user with id of :python:`user_id`. Gets every user with if they have their id in the set which is return by SQL subquery which get :python:`followed_id` where :python:`follower_id` is :python:`user_id`.

.. code-block:: python

	@users_app.route('/users_all')
	def users_all():
	    if session.get('logged_in')== None:
		return redirect(url_for("loginpage"))
	    with psycopg2.connect(current_app.config['dsn']) as conn:
		crs = conn.cursor()
		session_userid = session['user_id']
		crs.execute("select Id, username from users where Id !=%s",(session_userid,))
		conn.commit()
		fetched = crs.fetchall()
		crs.execute("select followed_id from user_follow where follower_id=%s",(session_userid,))
		conn.commit()
		follows=crs.fetchall()
		follows = [user[0] for user in follows]

	    return render_template('users_all.html', data = fetched,follows=follows)


This controller renders a page that lists all registered users. 
	1. First query selects every user except current one.
	2. Second query selects followed user and creates a list of them and passes it to page so that followed users can have "Unfollow"; unfollowed users can have "Follow" button next to their username in list.


