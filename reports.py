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
    return render_template("report.html",content_id=content_id,content=data)

@reports_app.route('/report_content/<content_id>',methods=["POST"])
def report_content(content_id):
    report_text = request.form['report_text']
    status ='pending'
    with psycopg2.connect(current_app.config['dsn']) as conn:
        crs = conn.cursor()
        crs.execute("insert into content_reports (report_id,user_id, image_id, report_comment, status, time) values (DEFAULT,%s, %s, %s, %s, now())",(1,content_id,report_text,status))
        conn.commit()
    return render_template("message.html",message="Content successfully reported.")

@reports_app.route('/issue_approval/<content_id>',methods=["POST"])
def issue_approval(content_id):
    with psycopg2.connect(current_app.config['dsn']) as conn:
        crs = conn.cursor()
        #crs.execute("delete from content_reports where image_id=%s",(content_id))
        crs.execute("delete from images where image_id = %s",(content_id)) # delete sorgusunu yaz
        conn.commit()
    return render_template("message.html",message="Content removed successfully.")

@reports_app.route('/issue_reject/<content_id>',methods=["POST"])
def issue_reject(content_id):
    with psycopg2.connect(current_app.config['dsn']) as conn:
        crs = conn.cursor()
        crs.execute("update content_reports set status='rejected' where image_id=%s",(content_id))
        conn.commit()
    return render_template("message.html",message="Report rejected.")