import os
import psycopg2
from flask import Flask
from flask import render_template, request
from flask import Blueprint, current_app


gmessage_app = Blueprint('gmessage_app', __name__)


@gmessage_app.route('/gmessage',methods=["POST"])
def gmessage():
    gmessage = request.form['gmessage']
    sender = request.form['senders']
    receiver = request.form['receivers']
    with psycopg2.connect(current_app.config['dsn']) as conn:
            crs=conn.cursor()
            crs.execute("insert into messages (time, message) values (now(), %s)RETURNING message_id", (gmessage,))
            m_id = crs.fetchone()[0]
            crs.execute("select ID from users where username=%s", (sender,))
            sndr_id = crs.fetchone()
            crs.execute("insert into senders (sender_id, message_id) values (%s, %s)", (sndr_id,m_id))
            crs.execute("select ID from users where username=%s", (receiver,))
            rcvr_id = crs.fetchone()
            crs.execute("insert into receivers (receiver_id, message_id) values (%s, %s)", (rcvr_id,m_id))
            data = conn.commit()

    return render_template('message.html', message = "Message has been sent.")

@gmessage_app.route('/gmessage_delete/<id>')
def gmessage_delete(id):
    with psycopg2.connect(current_app.config['dsn']) as conn:
            crs=conn.cursor()
            crs.execute("delete from messages where message_id = %s", (id))
            crs.execute("delete from senders where message_id = %s", (id))
            crs.execute("delete from receivers where message_id = %s", (id))
            data = conn.commit()

    return render_template('message.html', message = "Message has been deleted.")

@gmessage_app.route("/gmessage_update/<id>",methods=["POST"])
def gmessage_update(id):
    updated_gmessage = request.form["new_gmessage"]
    with psycopg2.connect(current_app.config["dsn"]) as conn:
        crs = conn.cursor()
        crs.execute('update messages set time=now(),message=%s where message_id=%s ',(updated_gmessage,id))
        conn.commit()

    return render_template("message.html",message="Message has been updated.")
