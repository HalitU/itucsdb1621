import psycopg2

from flask import Blueprint, current_app, render_template, session, request, redirect, url_for

groups_app = Blueprint('groups_app', __name__)

@groups_app.route('/create_group')
def create_group():
    if not session.get('user_id'):
        return redirect(url_for('home_page'))

    with psycopg2.connect(current_app.config['dsn']) as conn:
        crs = conn.cursor()
        crs.execute("select * from users where ID in (select followed_id from user_follow where follower_id = %s)", (session['user_id'],))
        conn.commit()
        data = crs.fetchall()

    return render_template('listfollowed.html', data=data)
@groups_app.route('/addtogroup',  methods = ['POST'])
def addtogroup():
    name = request.form['name']
    desc = request.form['desc']
    members = request.form.getlist('members')

    with psycopg2.connect(current_app.config['dsn']) as conn:
        crs = conn.cursor()
        crs.execute("insert into user_groups (group_name, gp_path, group_exp) values (%s, %s, %s) returning group_id", (name, "/", desc))
        conn.commit()
        data = crs.fetchone()
        id = data[0]

        for m in members:
            crs.execute("insert into group_members(group_id, user_id, time, member_status, role) values (%s, %s, now(), 'active', 'admin')", (id, m))
            conn.commit()

    return redirect(url_for('groups_app.show_group', group_id = id))

@groups_app.route('/show_group/<group_id>')
def show_group(group_id):
    with psycopg2.connect(current_app.config['dsn']) as conn:
        crs = conn.cursor()
        crs.execute("select u.username, u.id from group_members as g inner join users as u on u.id = g.user_id where group_id = %s", (group_id, ))
        memberdata = crs.fetchall()
        crs.execute("select group_name, gp_path, group_exp from user_groups where group_id = %s", (group_id,))
        data = crs.fetchone()
        conn.commit()
    return render_template('groupinfo.html', data=data, memberdata=memberdata)    # bu rotaya gelen kişiler şablonun içinin veri tabanından alınmış verilerle doldurulmuş halini görsünler

@groups_app.route('/delete_member/<id>')
def delete_member(id):
    with psycopg2.connect(current_app.config['dsn']) as conn:
        crs = conn.cursor()
        crs.execute("delete from group_members where user_id = %s", id)
        conn.commit()
    return render_template('message.html', message="Successfully removed.")