import os
import psycopg2
from flask import Flask
from flask import render_template, request
from flask import Blueprint, current_app

#declaring sub app with blueprint
notific_app = Blueprint('notific_app', __name__)

@notific_app.route('/notification_delete/<id>')
def notification_delete(id):
    with psycopg2.connect(current_app.config['dsn']) as conn:           
            crs=conn.cursor()
            crs.execute("delete from notifications where notification_id = %s", (id))
            data = conn.commit()
    
    return render_template('message.html', message = "Notification deleted..")

@notific_app.route('/status_update/', methods = ['GET'])
def status_update():
    id = request.args.get('id')
    stat = request.args.get('status')
    with psycopg2.connect(current_app.config['dsn']) as conn:           
            crs=conn.cursor()
            if stat == "False":
                crs.execute("update notifications set read_status = TRUE where notification_id = %s", (id))
            elif stat == "True": 
                crs.execute("update notifications set read_status = FALSE where notification_id = %s", (id))
            data = conn.commit()
    
    return render_template('message.html', message = "Notification status updated..")