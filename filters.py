import psycopg2
from flask import Flask
from flask import render_template, request, jsonify
from flask import Blueprint, current_app

#declaring sub app with blueprint
filters_app = Blueprint('filters_app', __name__)

@filters_app.route('/filter/index')
def index():
    session_user_id = 1

    with psycopg2.connect(current_app.config['dsn']) as conn:           
        crs = conn.cursor()
        crs.execute("select id,name from image_filter where user_id = %s", (session_user_id,))
        data = crs.fetchall()

    return render_template('filter_index.html', list = data)

@filters_app.route('/filter/fetch/<id>')
def fetch(id):

    session_user_id = 1

    with psycopg2.connect(current_app.config['dsn']) as conn:           
        crs = conn.cursor()
        crs.execute("select * from image_filter where user_id = %s and id = %s", (session_user_id,id))
        data = crs.fetchone()

    return jsonify(data)

@filters_app.route('/filter/delete/<id>')
def delete(id):
    session_user_id = 1

    with psycopg2.connect(current_app.config['dsn']) as conn:           
        crs = conn.cursor()
        crs.execute("select * from image_filter where user_id = %s and id = %s", (session_user_id,id))
        data = crs.fetchone()
        if data:
            crs.execute("delete from image_filter where user_id = %s and id = %s", (session_user_id, id))
            conn.commit()
        else:
            return render_template('message.html', message = "No record has found.")

    return render_template('message.html', message = "filter deleted")

@filters_app.route('/filter/update')
def update():
    session_user_id = 1

    with psycopg2.connect(current_app.config['dsn']) as conn:           
        crs = conn.cursor()
        crs.execute("select * from image_filter where user_id = %s and id = %s", (session_user_id,id))
        data = crs.fetchone()
        #update        
    return jsonify(False)