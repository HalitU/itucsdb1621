import psycopg2

from flask import Blueprint, current_app, render_template, request, session, redirect, url_for

events_app = Blueprint('events_app', __name__)

@events_app.route('/show_events')
def show_events():
    if session.get('logged_in')== None:
        return redirect(url_for("loginpage"))
    with psycopg2.connect(current_app.config['dsn']) as conn:
        crs = conn.cursor()
        crs.execute("select event_name, event_exp, event_time, event_id from events")
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
    return redirect(url_for('events_app.show_events'))

@events_app.route('/delete_event/<id>')
def delete_event(id):
    with psycopg2.connect(current_app.config['dsn']) as conn:
        crs = conn.cursor()
        crs.execute("delete from events where event_id = %s", (id, ))
        conn.commit()
    return redirect(url_for('events_app.show_events'))
@events_app.route('/updateform')
def updateform():
    return render_template('update_event.html')

@events_app.route('/update_event',methods=["POST"])
def update_event():
    old_name = request.form["old-name"]
    new_name = request.form["event-name"]
    explan = request.form["event-exp"]
    time_event = request.form["event-time"]
    with psycopg2.connect(current_app.config['dsn']) as conn:
        crs = conn.cursor()
        crs.execute("update events set event_name=%s, event_exp=%s, event_time=%s where event_name = %s", (new_name, explan, time_event, old_name, ))

    return redirect(url_for('events_app.show_events'))