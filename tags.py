import psycopg2
from flask import Flask
from flask import render_template, request
from flask import Blueprint, current_app,session,redirect, url_for

#declaring sub app with blueprint
tags_app = Blueprint('tags_app', __name__)

@tags_app.route('/add_tag/<photo_id>/', methods=["POST"])
def add_tag(photo_id):
    # a post request would be more elegant
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

@tags_app.route('/delete_tag/<photo_id>/', methods=["POST"])
def delete_tag(photo_id,):
    tagged_id=request.form["_id"]
    with psycopg2.connect(current_app.config['dsn']) as conn:
        crs = conn.cursor()
        ## if null show and error message
        print(tagged_id)
        crs.execute("delete from tags where tagger_id=%s and tagged_id=%s and photo_id=%s  ",(session["user_id"],tagged_id,photo_id))
        conn.commit()
    return render_template('message.html',message="Successfully deleted tag")

## no use
@tags_app.route('/retrieve_tags/<photo_id>/')
def retrieve_tags(photo_id):
    with psycopg2.connect(current_app.config['dsn']) as conn:
        crs = conn.cursor()
        crs.execute("select *  from tags where photo_id=%s  ",(photo_id))
        conn.commit()
    return render_template('message.html',message="Successfully added tag")


