import psycopg2
from flask import Flask
from flask import render_template, request
from flask import Blueprint, current_app,session,redirect, url_for

#declaring sub app with blueprint
tags_app = Blueprint('tags_app', __name__)

@tags_app.route('add_tag/<photo_id>/<username>')
def add_tag(photo_id,username):
    pass

@tags_app.route('update_tag/<photo_id>/<username>')
def update_tag(photo_id,username):
    pass

@tags_app.route('delete_tag/<photo_id>/<username>')
def delete_tag(photo_id,username):
    pass

@tags_app.route('retrieve_tags/<photo_id>/')
def retrieve_tags(photo_id):
    pass


