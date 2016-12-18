import psycopg2

from flask import Blueprint, current_app, render_template, request

events_app = Blueprint('events_app', __name__)

@events_app.route('/show_events')
def show_events():
    if session.get('logged_in')== None:
        return redirect(url_for("loginpage"))
    with psycopg2.connect(current_app.config['dsn']) as conn:
        crs = conn.cursor()
        crs.execute("select event_name, event_exp, event_time from events")
        conn.commit()
        data = crs.fetchall()
    return render_template('allevents.html', data=data)

@events_app.route('/create_event', methods = ['POST'])
def create_event():
    new_name = request.form["event-name"]
    explan = request.form["event-exp"]
    time_event = request.form["event-time"]
    with psycopg2.connect(current_app.config['dsn']) as conn:
        crs = conn.cursor()
        crs.execute("insert into events (event_name, event_exp, event_time) values (%s, %s, %s)", (new_name, explan, time_event))
        conn.commit()
    return render_template("message.html", message="Successfully created")

