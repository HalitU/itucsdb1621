import psycopg2

from flask import Blueprint, current_app, render_template

events_app = Blueprint('events_app', __name__)

@events_app.route('/show_events')
def show_events():
    with psycopg2.connect(current_app.config['dsn']) as conn:
        crs = conn.cursor()
        crs.execute("select event_name, event_exp, event_time from events")
        conn.commit()
        data = crs.fetchall()
    return render_template('allevents.html', data=data)

