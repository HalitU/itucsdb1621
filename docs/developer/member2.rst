.. raw:: html

	<style> .danger{color:red} </style>


Parts Implemented by Rumeysa Bulut
==================================

User operations, event organizing, and creating groups is implemented by me.

General Database Design
-----------------------

.. figure:: member2er.png

	ENTITY-RELATIONSHIP DIAGRAM OF MY PART

User Operations
---------------

Database Design
^^^^^^^^^^^^^^^

.. code-block:: sql

	CREATE TABLE IF NOT EXISTS users(
		ID serial primary key,
		username VARCHAR(50) NOT NULL,
		password text NOT NULL,
		photo_path text,
		email text NOT NULL UNIQUE
	);



Users table has a serial primary key. This table is used by all members of the project.


Controller Code
^^^^^^^^^^^^^^^
.. code-block:: python

	from flask import Blueprint, current_app, render_template, request, session, redirect, url_for
	from passlib.hash import sha256_crypt
	register_app = Blueprint('register_app', __name__)

We used Flask's Blueprint interface. Blueprint simplifies large application works by allowing us to separate the project into different files.

.. code-block:: python

	@register_app.route('/signup', methods = ['POST'])
	def signup():
		data_username = request.form["username"]
		data_password = sha256_crypt.encrypt(request.form["password"])
		data_email = request.form["email"]
		print(data_password)
		with psycopg2.connect(current_app.config['dsn']) as conn:
			crs = conn.cursor()
			crs.execute("select username, email from users")
			data=crs.fetchall()
			for d in data:
				if d[0] == data_username:
					return render_template('message.html', message="The username is already exists")
				elif d[1] == data_email:
					return render_template('message.html', message="The email is already exists")

			crs.execute("insert into users (username, password, email) values (%s, %s, %s)",(data_username,data_password,data_email))
			conn.commit()

		return render_template('message.html', message="Successfully registered")


This register section gets user information from signup.html. It hashes the password, and checks user name and email whether they exists or not. If information satisfy the conditions, it adds the user to the database.
	
	* A disposable connection to database server is created via 'with' command which gets configuration from main application(current_app) settings.
	* Creates a cursor.
	* Executes an SQL selection.
	* Checks the data_username and data_email.
	* Executes an SQL insertion.
	* Commits the changes and save the result of the operation.

If the conditions fail in the control stage or the insertion is done successfully, function returns a rendered template message.html which says the result of the user action.

.. code-block:: python

	@register_app.route('/login', methods=["POST"])
	def login():
		data_username = request.form["username"]
		data_password = sha256_crypt.encrypt(request.form["password"])

		with psycopg2.connect(current_app.config['dsn']) as conn:
			crs = conn.cursor()
			crs.execute("select ID from users where username = %s", (data_username, ))
			userid = crs.fetchone()

			if userid:
				crs.execute("select password, ID from users where username = %s", (data_username,))
				conn.commit()
				data = crs.fetchone()

			else:
				return render_template('message.html', message="Invalid Credentials")
			if (sha256_crypt.verify(request.form["password"],data[0])):
				session['logged_in'] = True
				session['user_id'] = data[1]
				return redirect(url_for('home_page'))
			else:
				return render_template('login.html')

 Login section proceeds in a similar way to sign up operation. It controls the username and password are registered.
	
	* Creates a cursor.
	* Executes an SQL select to check the user is registered before.
	* If user is in the database, it gets the password and checks it.
	* Makes session changes.

The function returns the necessary pages under certain conditions. If username fails, a message says Invalid Credentials will be appear. If password fails, returns back to the login page. If entered information is true, directs users to the home page.

.. code-block:: python

	@register_app.route('/update_user',methods=["POST"])
	def updateUser():
		id=session['user_id']
		data_username = request.form["username"]
		data_password = sha256_crypt.encrypt(request.form["password"])
		data_email = request.form["email"]


		with psycopg2.connect(current_app.config['dsn']) as conn:
			crs = conn.cursor()
			crs.execute("update users set username=%s, password=%s,email=%s where ID = %s",(data_username,data_password,data_email,id))

		return render_template('message.html',message="Successfully updated")


This register section gets user information from update.html. If users want to update their information, this function gets current information from the form and the user ID from session.

	* The function connects to the database driver.
	* Creates a cursor
	* Executes an SQL update with id.

Then returns a "message.html" template which says "Successfully updated."

.. code-block:: python

	@register_app.route('/remove_user',methods=["POST"])
	def removeUser():
		data_username = request.form["username"]
		with psycopg2.connect(current_app.config['dsn']) as conn:
			crs = conn.cursor()
			crs.execute("delete from users where username = %s",(data_username,))
			data = conn.commit()

		return render_template('login.html')

Deleting an account almost follows the same process with update section.
	
	* The function connects to the database driver.
	* Creates a cursor.
	* Executes an SQL delete with username.
	* Commits the changes to the database.

The function returns to the login page.


User Groups
-----------

Database Design
^^^^^^^^^^^^^^^

.. code-block:: sql

	CREATE TABLE IF NOT EXISTS user_groups(
		group_id serial primary key,
		group_name text,
		gp_path text,
		group_exp text
	);


Controller Code
^^^^^^^^^^^^^^^

.. code-block:: python

	@groups_app.route('/create_group')
	def create_group():
		if not session.get('user_id'):
			return redirect(url_for('home_page'))

		with psycopg2.connect(current_app.config['dsn']) as conn:
			crs = conn.cursor()
			crs.execute("select * from users where ID in (select followed_id from user_follow where follower_id = %s)", (session['user_id'],))
			conn.commit()
			data = crs.fetchall()

		return render_template('listfollowed.html', data=data)

Creating groups feature is activated after users logged in. When users click the new group icon on the dropdown menu, a new page will be appear. On this page, all people they followed will be listed. They can determine the group name and the group description. Then, they can select the members of the group among the listed people.
	
	* At first, the function controls the session.
	* If user is logged in, it connects to the database.
	* Creates a cursor.
	* Executes an SQL select query to list the followed users.

The function returns to the group creation page.

.. code-block:: python

	@groups_app.route('/addtogroup',  methods = ['POST'])
	def addtogroup():
		name = request.form['name']
		desc = request.form['desc']
		members = request.form.getlist('members')

		with psycopg2.connect(current_app.config['dsn']) as conn:
			crs = conn.cursor()
			crs.execute("insert into user_groups (group_name, gp_path, group_exp) values (%s, %s, %s) returning group_id", (name, "/", desc))
			conn.commit()
			data = crs.fetchone()
			id = data[0]

			for m in members:
				crs.execute("insert into group_members(group_id, user_id, time, member_status, role) values (%s, %s, now(), 'active', 'admin')", (id, m))
				conn.commit()

		return redirect(url_for('groups_app.show_group', group_id = id))

This function does the main job. Creating group with specified name and description and adding the selected users to this group is processed in this function.
	
	* It gets the information from the form that is in the previous stage.
	* Then connects to the database and creates a cursor.
	* It inserts the group with name and description with an SQL insert and gets the group id.
	* At last, it inserts the selected users into the created group.

After the operation is done, it returns to the page which shows the newly created group.

.. code-block:: python

	@groups_app.route('/show_group/<group_id>')
	def show_group(group_id):
		with psycopg2.connect(current_app.config['dsn']) as conn:
			crs = conn.cursor()
			crs.execute("select u.username, u.id from group_members as g inner join users as u on u.id = g.user_id where group_id = %s", (group_id, ))
			memberdata = crs.fetchall()
			crs.execute("select group_name, gp_path, group_exp from user_groups where group_id = %s", (group_id,))
			data = crs.fetchone()
			conn.commit()
		return render_template('groupinfo.html', data=data, memberdata=memberdata)

This function shows only the group which has been just created.
	
	* It gets the group id from the previous function, addtogroup.
	* The function does 2 SQL select query to list the group and its members.

It returns to the groupinfo.html to display the group information with its members.

.. code-block:: python

	@groups_app.route('/allgroups')
	def allgroups():
		with psycopg2.connect(current_app.config['dsn']) as conn:
			crs = conn.cursor()
			crs.execute("select group_name, group_exp, group_id from user_groups")
			data = crs.fetchall()
			crs.execute("select u.username, u.id from group_members as g inner join users as u on u.id = g.user_id")
			memberdata = crs.fetchall()
		return render_template('allgroups.html',data=data,memberdata=memberdata)

Users can list the current groups by clicking the groups icon on the dropdown menu.
	
	* The function selects all groups and their members.
	
It sends the group data and member data to allgroups.html.

.. code-block:: python

	@groups_app.route('/delete_member/<id>')
	def delete_member(id):
		with psycopg2.connect(current_app.config['dsn']) as conn:
			crs = conn.cursor()
			crs.execute("delete from group_members where user_id = %s", id)
			conn.commit()
		return render_template('message.html', message="Successfully removed.")

Users can delete a member from a group after they create the group by clicking cross sign.
	
	* It gets id.
	* Performs the delete operation according to the id.

Then the function returns a rendered template message.html which gives a message that says removing is successful.

.. code-block:: python

	@groups_app.route('/delete_group/<id>')
	def delete_group(id):
		with psycopg2.connect(current_app.config['dsn']) as conn:
			crs = conn.cursor()
			crs.execute("delete from user_groups where group_id = %s", (id, ))
			conn.commit()
		return redirect(url_for('groups_app.allgroups'))

Users also delete a group by clicking the cross sign in the page which lists all groups.
	
	* It gets the id.
	* Performs delete operation.

Then it returns to the page lists all groups.

.. code-block:: python

	@groups_app.route('/updateform')
	def updateform():
		return render_template('update_group.html')

	@groups_app.route('/update_group',methods=["POST"])
	def update_group():
		old_name = request.form['oldname']
		new_name = request.form['name']
		desc = request.form['desc']
		with psycopg2.connect(current_app.config['dsn']) as conn:
			crs = conn.cursor()
			crs.execute("update user_groups set group_name=%s, group_exp=%s where group_name = %s", (new_name, desc, old_name, ))

		return redirect(url_for('groups_app.allgroups'))

This 2 functions allow the users to update their groups name and description. First one returns to the update_group.html to get the current information. Second one gets the information from the update_group.html.
	
	* Second one connects to the database.
	* It performs the update operation with an SQL update.

Then it redirects to the page that lists all groups.


Events
------

Database Design
^^^^^^^^^^^^^^^

.. code-block:: sql

	CREATE TABLE IF NOT EXISTS events(
		event_id serial primary key,
		event_name text,
		event_time text,
		event_exp text
	);

Controller Code
^^^^^^^^^^^^^^^

.. code-block:: python

	@events_app.route('/create_event', methods = ['POST'])
	def create_event():
		new_name = request.form["event-name"]
		explan = request.form["event-exp"]
		time_event = request.form["event-time"]
		with psycopg2.connect(current_app.config['dsn']) as conn:
			crs = conn.cursor()
			crs.execute("insert into events (event_name, event_exp, event_time) values (%s, %s, %s)", (new_name, explan, time_event))
			conn.commit()
		return redirect(url_for('events_app.show_events'))

create_event function allows the users to organize new events. It works quite similar to the create_group function. Users can use this feature by clicking the new event icon on the dropdown menu.
	
	* It gets the data from the form.
	* Connects to the database.
	* Creates a cursor.
	* Executes an SQL insertion to create the event.

Then, the function redirects to the page which shows all events with their information.

.. code-block:: python

	@events_app.route('/show_events')
	def show_events():
		if session.get('logged_in')== None:
			return redirect(url_for("loginpage"))
		with psycopg2.connect(current_app.config['dsn']) as conn:
			crs = conn.cursor()
			crs.execute("select event_name, event_exp, event_time, event_id from events")
			conn.commit()
			data = crs.fetchall()
		return render_template('allevents.html', data=data)

Users can display the events they created. This feature is activated after users logged in as in the user groups sections.
	
	* It controls the session.
	* If the user is logged in, it executes an SQL select query.

It sends the data to the allevents.html to show all events with their information.

.. code-block:: python

	@events_app.route('/delete_event/<id>')
	def delete_event(id):
		with psycopg2.connect(current_app.config['dsn']) as conn:
			crs = conn.cursor()
			crs.execute("delete from events where event_id = %s", (id, ))
			conn.commit()
		return redirect(url_for('events_app.show_events'))

Deleting an event is also possible. Users can delete the event by clicking the cross sign. Thus, the function gets the event id.
	
	* Connects to the database.
	* Creates a cursor.
	* Executes an SQL deletion to remove the event from the database using id.

Then, the function redirects to the page which shows all events with their information.

.. code-block:: python

	@events_app.route('/updateEvent')
	def updateEvent():
		return render_template('update_event.html')

	@events_app.route('/update_event',methods=["POST"])
	def update_event():
		old_name = request.form["old-name"]
		new_name = request.form["event-name"]
		explan = request.form["event-exp"]
		time_event = request.form["event-time"]
		with psycopg2.connect(current_app.config['dsn']) as conn:
			crs = conn.cursor()
			crs.execute("update events set event_name=%s, event_exp=%s, event_time=%s where event_name = %s", (new_name, explan, time_event, old_name, ))

		return redirect(url_for('events_app.show_events'))

Updating the event also works very similar to the group section. After the pencil icon is clicked, a form page comes to the screen. Users can fulfill the form with current information. Second function does the main work.
	
	* It gets data from the from.
	* Connects to the database.
	* Creates a cursor.
	* Executes an SQL update operation to renew the event.
	
Then, the function redirects to the page which shows all events with their information.




