from flask import render_template, request, jsonify
from flask import Blueprint, current_app
import psycopg2

reports_app = Blueprint("reports_app",__name__)

@reports_app.route('/initiate_report/<content_id>')
def initiate_report(content_id):

    with psycopg2.connect(current_app.config['dsn'])  as conn:
        crs = conn.cursor()
        crs.execute("select path from images where image_id=%s",(content_id))
        conn.commit()
        data = crs.fetchone()
    print(content_id)
    print(data[0])
    return render_template("report.html",content_id=content_id,content=data)

@reports_app.route('/report_content/<content_id>',methods=['POST'])
def report_content(content_id):
    report_text = request.form["report_text"]
    status ="pending"
    with psycopg2.connect(current_app.config['dsn']) as conn:
        crs = conn.cursor()
        crs.execute("insert into content_reports (user_id,image_id,text,status,time) values (%s,%s,%s,%s,now())",(2,content_id,report_text,status))
        conn.commit()
    return render_template("messages.html",message="Content successfully reported")

@reports_app.route('/show_content_reports')
def show_content_reports():
    with psycopg2.connect(current_app.config['dsn']) as conn:
        crs = conn.cursor()
        crs.execute("select (user_id,image_id,text,status,time) from content_reports order by time")
        conn.commit()
        data = crs.fetchall()
    return render_template("issues.html",data=data)

@reports_app.route('/issue_approval/<content_id>')
def issue_approval(content_id):
    with psycopg2.connect(current_app.config['dsn']) as conn:
        crs = conn.cursor()
        crs.execute("update content_reports set status='approved' where content_id=%s",(content_id))
        crs.execute("delete") # delete sorgusunu yaz home html deki bootstrap i düzelt
        conn.commit()
    return render_template("message.html",message="Content removed successfully")

@reports_app.route('/issue_reject/<content_id>')
def issue_reject(content_id):
    with psycopg2.connect(current_app.config['dsn']) as conn:
        crs = conn.cursor()
        crs.execute("update content_reports set status='rejected' where content_id=%s",(content_id))
        conn.commit()
    return render_template("issues.html",data=data)