
import psycopg2
from flask import Blueprint, current_app, render_template, request, session, redirect, url_for
from passlib.hash import sha256_crypt
register_app = Blueprint('register_app', __name__)

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


@register_app.route('/remove_user',methods=["POST"])
def removeUser():
    data_username = request.form["username"]
    with psycopg2.connect(current_app.config['dsn']) as conn:
        crs = conn.cursor()
        crs.execute("delete from users where username = %s",(data_username,))
        data = conn.commit()

    return render_template('login.html')

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
