import os
import psycopg2
from flask import Flask
from flask import render_template, request
from flask import Blueprint, current_app

#declaring sub app with blueprint
comment_app = Blueprint('comment_app', __name__)


@comment_app.route('/comment/<user_id>/<image_id>', methods = ['POST'])
def comment(user_id,image_id):
    ## insert
    comment = request.form['comment']
    with psycopg2.connect(current_app.config['dsn']) as conn:
            crs=conn.cursor()
            crs.execute("insert into comments (user_id, image_id, time, text) values (%s, %s, now(), %s)", (user_id, image_id, comment))
            data = conn.commit()

    return render_template('message.html', message = "Successfully commented..")

@comment_app.route('/comment_delete/<id>')
def comment_delete(id):
    ## delete
    #id = request.args.get('id')
    with psycopg2.connect(current_app.config['dsn']) as conn:
            crs=conn.cursor()
            crs.execute("delete from comments where comment_id = %s", (id))
            data = conn.commit()

    return render_template('message.html', message = "Comment deleted..")