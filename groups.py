import psycopg2

from flask import Blueprint, current_app, render_template

groups_app = Blueprint('groups_app', __name__)

@groups_app.route('/show_group/<group_id>')
def show_group(group_id):
    with psycopg2.connect(current_app.config['dsn']) as conn:
        crs = conn.cursor()
        crs.execute("select * from group_members where group_id = %s", (group_id, ))
        memberdata = crs.fetchall()
        crs.execute("select group_name, gp_path, group_exp from user_groups")
        data = crs.fetchone()
        conn.commit()
    return render_template('groupinfo.html', data=data, memberdata=memberdata)    # bu rotaya gelen kişiler şablonun içinin veri tabanından alınmış verilerle doldurulmuş halini görsünler

@groups_app.route('/delete_member/<user_id>')
def delete_member(user_id):
    with psycopg2.connect(current_app.config['dsn']) as conn:
        crs = conn.cursor()
        crs.execute("delete from group_members where user_id = %s", (user_id, ))
        conn.commit()
    return render_template('message.html', message="Successfully removed.")