import os
import psycopg2
from flask import Flask
from flask import render_template, request
from flask import Blueprint, current_app

#declaring sub app with blueprint
bidding_app = Blueprint('bidding_app', __name__)

@bidding_app.route('/add_new_bid/', methods = ['POST'])
def add_new_bid():
    name = request.form['item_name']
    details = request.form['description']
    image = request.files['image']
    price = request.form['price']
    seller_id = 1
    current_holder = 1

    image.save(os.path.join('static/uploads', image.filename))
    
    with psycopg2.connect(current_app.config['dsn']) as conn:    
            crs=conn.cursor()
            crs.execute("insert into images (user_id, path, time, text) values (%s, %s, now(), %s) RETURNING image_id", (2, image.filename, details))
            im_id = crs.fetchone()
            print(im_id[0])
            crs.execute("insert into bids (header, details, image, current_price, seller_id, current_holder) values (%s, %s, %s, %s, %s, %s)", (name, details, im_id[0], price, seller_id, current_holder))
            conn.commit()

    return render_template('message.html', message = "Bid Successfully Added!")

@bidding_app.route('/update_bid/<id>', methods = ['POST'])
def update_bid(id):
    new_price = request.form['price']
    with psycopg2.connect(current_app.config['dsn']) as conn:

        crs=conn.cursor()
        crs.execute("select current_price from bids where bid_id=%s", (id))
        data = crs.fetchone()

        if data[0] > float(new_price):
            return render_template('message.html', message = "You need to bid a higher price from current one!")

        crs.execute("update bids set current_price=%s where bid_id=%s",(new_price, id))
        conn.commit()

    return render_template('message.html', message = "You bid successfully applied!")

@bidding_app.route('/delete_bid/<id>')
def delete_bid(id):
    with psycopg2.connect(current_app.config['dsn']) as conn:
        crs=conn.cursor()
        crs.execute("delete from bids where bid_id=%s",(id))
        conn.commit()
    return render_template('message.html', message = "Your bid is successfully removed!")    