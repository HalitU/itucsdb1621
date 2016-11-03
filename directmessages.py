import os
import psycopg2
from flask import Flask
from flask import render_template, request
from flask import Blueprint, current_app


dmessage_app = Blueprint('dmessage_app', __name__)


@dmessage_app.route('/dmessage',methods=["POST"])
def dmessage():
    print("message adding")
    dmessage = request.form['dmessage']
    with psycopg2.connect(current_app.config['dsn']) as conn:
            crs=conn.cursor()
            crs.execute("insert into directmessages (sender_id, receiver_id, time, dmessage) values (%s, %s, now(), %s)", (1, 2, dmessage))
            data = conn.commit()

    return render_template('message.html', message = "Message has been sent.")

@dmessage_app.route('/dmessage_delete/<id>')
def dmessage_delete(id):
    with psycopg2.connect(current_app.config['dsn']) as conn:
            crs=conn.cursor()
            crs.execute("delete from directmessages where dmessage_id = %s", (id))
            data = conn.commit()

    return render_template('message.html', message = "Message has been deleted.")

@dmessage_app.route("/dmessage_update/<id>",methods=["POST"])
def dmessage_update(id):
    updated_dmessage = request.form["new_dmessage"]
    with psycopg2.connect(current_app.config["dsn"]) as conn:
        crs = conn.cursor()
        crs.execute('update directmessages set time=now(),dmessage=%s where dmessage_id=%s ',(updated_dmessage,id))
        conn.commit()

    return render_template("message.html",message="Message has been updated.")