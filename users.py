import psycopg2
from flask import Flask
from flask import render_template, request
from flask import Blueprint, current_app,session,redirect, url_for

#declaring sub app with blueprint
users_app = Blueprint('users_app', __name__)

#DONE
@users_app.route('/search_user/',methods=['GET'])
def search_user():
    with psycopg2.connect(current_app.config['dsn']) as conn:
        username = request.args.get('username')
        if(username == ""):
            username = " "
        print(type(username))
        crs = conn.cursor()
        crs.execute("select ID,username,photo_path from users where username like %s",(username,))
        print(username)
        conn.commit()
        result = crs.fetchall()
    return render_template('search_results.html',result=result)


@users_app.route('/show_profile/<user_id>')
def show_profile(user_id):
    with psycopg2.connect(current_app.config['dsn']) as conn:
        crs = conn.cursor()
        crs.execute("select ID,username,photo_path,email from users where ID = %s",(user_id))
        conn.commit()
        result = crs.fetchone()
        crs.execute("select * from user_follow where follower_id=%s and  followed_id=%s",(session.get("user_id"),user_id))
        conn.commit()
        follow_query=crs.fetchone()
        is_following = False if follow_query == None else True
        is_self = False 
        if int(user_id) == session.get("user_id"):
            is_self = True # can not follow oneself
        crs.execute("select path from images where user_id =%s",(user_id))
        conn.commit()
        list_photos = crs.fetchall()
    return render_template('profile.html',result=result,is_following=is_following,is_self=is_self,list_photos=list_photos)

@users_app.route('/user_follow/<followed>')
def user_follow(followed):
     with psycopg2.connect(current_app.config['dsn']) as conn:
        crs = conn.cursor()
        crs.execute("insert into user_follow (follower_id,followed_id,time) values (%s,%s,now())",(session["user_id"],followed))
        conn.commit()
     return render_template('message.html',message="Successfully followed")

@users_app.route('/user_unfollow/<followed>')
def user_unfollow(followed):
    with psycopg2.connect(current_app.config['dsn']) as conn:
        crs = conn.cursor()
        crs.execute("delete from user_follow where follower_id=%s and followed_id=%s",(session["user_id"],followed))
        conn.commit()
    return render_template('message.html',message="Successfully unfollowed")
#DONE

@users_app.route('/show_followers/<user_id>')
def show_followers(user_id):
    with psycopg2.connect(current_app.config['dsn']) as conn:
        crs = conn.cursor()
        crs.execute("select ID,username,photo_path from users where ID in (SELECT follower_id from user_follow where followed_id = %s)",(user_id,))
        conn.commit()
        ulist =crs.fetchall()
    return render_template('user_list.html',ulist=ulist,user_id=user_id)

@users_app.route('/show_followed/<user_id>')
def show_followed(user_id):
    with psycopg2.connect(current_app.config['dsn']) as conn:
        crs = conn.cursor()
        crs.execute("select ID,username,photo_path from users where ID in (SELECT followed_id from user_follow where follower_id = %s)",(user_id,))
        conn.commit()
        ulist =crs.fetchall()
    return render_template('user_list.html',ulist=ulist,user_id=user_id)

@users_app.route('/user_block/<user_id>')
def user_block(user_id):
    session_userid = session["user_id"] # it will be change when the session is implemented
    with psycopg2.connect(current_app.config['dsn']) as conn:
        crs = conn.cursor()
        crs.execute("select * from user_block where user_id = %s and blocked_id = %s",(session_userid, user_id))
        conn.commit()
        fetched =crs.fetchone()
        if fetched:
            return render_template('message.html', message="already blocked.")
        else:
            crs.execute("insert into user_block (user_id, blocked_id, time) values (%s, %s, now())", (session_userid, user_id))
            conn.commit()
        
    return redirect(url_for('users_app.users_all'))

@users_app.route('/user_deblock/<user_id>')
def user_deblock(user_id):
    session_userid = session["user_id"] # it will be change when the session is implemented
    with psycopg2.connect(current_app.config['dsn']) as conn:
        crs = conn.cursor()
        crs.execute("select * from user_block where user_id = %s and blocked_id = %s",(session_userid, user_id))
        conn.commit()
        fetched =crs.fetchone()
        if fetched:
            crs.execute("delete from user_block where user_id = %s and blocked_id = %s", (session_userid, user_id))
            conn.commit()    
        else:
            return render_template('message.html', message="you can't unblock user until block him")
    
    return redirect(url_for('users_app.users_all'))

@users_app.route('/users_all')
def users_all():
    if session.get('logged_in')== None:
        return redirect(url_for("loginpage"))
    with psycopg2.connect(current_app.config['dsn']) as conn:
        crs = conn.cursor()
        if session.get('logged_in') == True:
            session_userid = session['user_id']
            crs.execute("select Id, username from users where Id !=%s",(session_userid,))
        else:
            crs.execute("select Id, username from users")
        
        conn.commit()
        fetched = crs.fetchall()
        #print(fetched)
        crs.execute("select followed_id from user_follow where follower_id=%s",(session_userid,))
        conn.commit()
        follows=crs.fetchall()
        follows = [user[0] for user in follows]
        #print(follows)
        blocked = None

        if session.get('logged_in') == True:
            session_userid = session['user_id']
            crs.execute("select blocked_id from user_block where user_id = %s", (session_userid,))
            conn.commit()
            blocked = crs.fetchall()
            blocked = [user[0] for user in blocked]


    return render_template('users_all.html', data = fetched, blockdata = blocked,follows=follows)