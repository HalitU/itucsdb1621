import psycopg2
from flask import Flask
from flask import render_template, request, jsonify
from flask import Blueprint, current_app, redirect, url_for, session

#declaring sub app with blueprint
filters_app = Blueprint('filters_app', __name__)

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