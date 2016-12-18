import os
import psycopg2
from flask import Flask, session
from flask import render_template, request
from flask import Blueprint, current_app

#declaring sub app with blueprint
layout_app = Blueprint('layout_app', __name__)

@layout_app.route('/add_new_layout/', methods = ['POST'])
def add_new_layout():
    name = request.form['name']
    details = request.form['detail']
    font = request.form['font_name']
    font_size = request.form['font_size']
    bg_image = request.form['image_url']

    with psycopg2.connect(current_app.config['dsn']) as conn:    
            crs=conn.cursor()
            crs.execute("insert into premadelayouts (name, detail, font, font_size, bg_image_url) values (%s, %s, %s, %s, %s)", (name, details, font, font_size, bg_image))
            conn.commit()

    return render_template('message.html', message = "Layout Successfully Added!")

@layout_app.route('/layout_delete/<id>')
def layout_delete(id):
    with psycopg2.connect(current_app.config['dsn']) as conn:           
            crs=conn.cursor()
            crs.execute("delete from premadelayouts where layout_id = %s", (id))
            data = conn.commit()
    
    return render_template('message.html', message = "Layout deleted..")

@layout_app.route('/layout_update/<id>', methods = ['POST'])
def layout_update(id):
    name = request.form['name']
    details = request.form['detail']
    font = request.form['font_name']
    font_size = request.form['font_size']
    bg_image = request.form['image_url']

    with psycopg2.connect(current_app.config['dsn']) as conn:           
            crs=conn.cursor()
            crs.execute("update premadelayouts set name=%s, detail=%s, font=%s, font_size=%s, bg_image_url=%s where layout_id=%s",(name, details, font, font_size, bg_image, id))
            conn.commit()
    
    return render_template('message.html', message = "Layout updated..")

@layout_app.route('/layout_change/', methods = ['POST'])
def layout_change():
    lay_id = request.form['layout']
    with psycopg2.connect(current_app.config['dsn']) as conn:           
        crs=conn.cursor()
        crs.execute("select * from premadelayouts where layout_id = %s", (lay_id))
        data = crs.fetchone()
        session['bimg'] = data[5]
        session['font'] = data[3]
        session['font-size'] = data[4]
        conn.commit()
    return render_template('message.html', message = "Layout Changed.")