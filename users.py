import psycopg2
from flask import Flask
from flask import render_template, request
from flask import Blueprint, current_app

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
        crs.execute("select * from user_follow where follower_id=1 and  followed_id=%s",(user_id))
        conn.commit()
        follow_query=crs.fetchone()
        print(follow_query)
        is_following = False if follow_query == None else True
        is_self = False if (user_id==1) else True # can not follow oneself
        print(is_following)
        crs.execute("select path from images where user_id =%s",(user_id))
        conn.commit()
        list_photos = crs.fetchall()
    return render_template('profile.html',result=result,is_following=is_following,is_self=is_self,list_photos=list_photos)

@users_app.route('/user_follow/<follower>/<followed>')
def user_follow(follower,followed):
     with psycopg2.connect(current_app.config['dsn']) as conn:
        crs = conn.cursor()
        crs.execute("insert into user_follow (follower_id,followed_id,time) values (%s,%s,now())",(follower,followed))
        conn.commit()
     return render_template('message.html',message="Successfully followed")

@users_app.route('/user_unfollow/<follower>/<followed>')
def user_unfollow(follower,followed):
    with psycopg2.connect(current_app.config['dsn']) as conn:
        crs = conn.cursor()
        crs.execute("delete from user_follow where follower_id=%s and followed_id=%s",(follower,followed))
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
    session_userid = 1 # it will be change when the session is implemented
    with psycopg2.connect(current_app.config['dsn']) as conn:
        crs = conn.cursor()
        crs.execute("select * from users_block where user_id = %s and blocked_id = %s",(session_userid, user_id))
        conn.commit()
        fetched =crs.fetchone()
        if fetched:
            return render_template('message.html', message="already blocked.")
        else:
            crs.execute("insert into user_block (user_id, blocked_id, time) values (%s, %s, now())", (session_userid, user_id))
            conn.commit()
        
    return render_template('message.html', message = "user_blocked")

@users_app.route('/user_deblock/<user_id>')
def user_deblock(user_id):
    session_userid = 1 # it will be change when the session is implemented
    with psycopg2.connect(current_app.config['dsn']) as conn:
        crs = conn.cursor()
        crs.execute("select * from users_block where user_id = %s and blocked_id = %s",(session_userid, user_id))
        conn.commit()
        fetched =crs.fetchone()
        if fetched:
            crs.execute("delete from user_block where user_id = %s and blocked_id = %s", (session_userid, user_id))
            conn.commit()    
        else:
            return render_template('message.html', message="you can't unblock user until block him")
    
    return render_template('message.html', message= "user_unblocked")
