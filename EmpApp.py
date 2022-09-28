from flask import Flask, render_template, request
from pymysql import connections
from datetime import datetime
import os
import boto3
from config import *

app = Flask(__name__)

bucket = custombucket
region = customregion

db_conn = connections.Connection(
    host=customhost,
    port=3306,
    user=customuser,
    password=custompass,
    db=customdb

)
output = {}
table = 'employee'


@app.route("/", methods=['GET', 'POST'])
def home():
    return render_template('index.html')

@app.route("/about", methods=['POST'])
def about():
    return render_template('www.intellipaat.com')

@app.route("/login", methods=['GET','POST'])
def login():
    return render_template('login.html')

@app.route("/loginfirst", methods=['GET','POST'])
def loginfirst():
    return render_template('loginfirst.html')


@app.route("/aboutus", methods=['GET', 'POST'])
def aboutus():
    return render_template('aboutus.html')

@app.route("/mainpage", methods=['GET', 'POST'])
def mainpage():
    return render_template('mainpage.html')

@app.route("/database", methods=['GET', 'POST'])
def database():
    return render_template('databasemanagement.html')

@app.route("/contact", methods=['GET', 'POST'])
def contact():
    return render_template('contact.html')


@app.route("/AddEmp", methods=['GET', 'POST'])
def loadAddEmp():
    return render_template('AddEmp.html')

@app.route("/GetEmp", methods=['GET', 'POST'])
def loadGetEmp():
    return render_template('GetEmp.html')

@app.route("/displayseminar", methods=['GET', 'POST'])
def seminarattendee():
    db_conn = connections.Connection(
    host=customhost,
    port=3306,
    user=customuser,
    password=custompass,
    db=customdb)
    cursor = db_conn.cursor()
    cursor.execute("SELECT * FROM seminar")
    directoryData = cursor.fetchall()
    print(directoryData)
    cursor.close()
    return render_template('seminarregister.html',data = directoryData)

@app.route("/displayleave", methods=['GET', 'POST'])
def pendingLeave():
    db_conn = connections.Connection(
    host=customhost,
    port=3306,
    user=customuser,
    password=custompass,
    db=customdb)
    cursor = db_conn.cursor()
    cursor.execute("SELECT * FROM employee.leave WHERE status = 'Pending'")
    directoryData = cursor.fetchall()
    print(directoryData)
    cursor.close()
    cursor = db_conn.cursor()
    cursor.execute("SELECT * FROM employee.leave WHERE status = 'Approved.'")
    approveData = cursor.fetchall()
    print(approveData)
    cursor.close()
    cursor = db_conn.cursor()
    cursor.execute("SELECT * FROM employee.leave WHERE status = 'Rejected.'")
    rejectData = cursor.fetchall()
    print(rejectData)
    cursor.close()
    return render_template('leaveList.html',data = directoryData, approveData = approveData, rejectData=rejectData)

@app.route("/ApproveLeave", methods=['GET', 'POST'])
def ApproveLeave():
    db_conn = connections.Connection(
    host=customhost,
    port=3306,
    user=customuser,
    password=custompass,
    db=customdb)
    emp_id=request.args['approve_id']
    status = 'Approved.'
    update_sql = "UPDATE employee.leave SET status = %s WHERE emp_id = %s"
    cursor = db_conn.cursor()
    cursor.execute(update_sql, (status,emp_id))
    db_conn.commit()
    cursor.close()
    return render_template('success.html')

@app.route("/RejectLeave", methods=['GET', 'POST'])
def RejectLeave():
    db_conn = connections.Connection(
    host=customhost,
    port=3306,
    user=customuser,
    password=custompass,
    db=customdb)
    emp_id=request.args['reject_id']
    status = 'Rejected.'
    update_sql = "UPDATE employee.leave SET status = %s WHERE emp_id = %s"
    cursor = db_conn.cursor()
    cursor.execute(update_sql, (status,emp_id))
    db_conn.commit()
    cursor.close()
    return render_template('success.html')

@app.route("/registeremptoseminar", methods=['GET','POST'])
def AddEmpSeminar():
    emp_id = request.form['emp_id']
    name = request.form['name']
    department = request.form['department']

    insert_sql = "INSERT INTO seminar VALUES (%s, %s, %s)"
    cursor = db_conn.cursor()

    if emp_id == "":
        return "Please enter the required fields."
    
    if name == "":
        return "Please enter the required fields."

    try:

        cursor.execute(insert_sql, (emp_id,name, department))
        db_conn.commit()

    except Exception as e:
            return str(e)

    finally:
        cursor.close()

    print("all modification done...")
    return render_template('SeminarRegisterOutput.html', name=name)

@app.route('/withdrawSeminar', methods =['GET', 'POST'])
def withdrawSeminar():
     return render_template('withdrawSeminar.html')

@app.route('/seminarWithdraw', methods =['GET', 'POST'])
def seminarWithdraw():
    db_conn = connections.Connection(
    host=customhost,
    port=3306,
    user=customuser,
    password=custompass,
    db=customdb)
    cursor = db_conn.cursor()
    if request.method == 'POST':
        emp_id = request.form["emp_id"]
        select_emp = "SELECT * FROM seminar WHERE emp_id = %(emp_id)s"
        cursor.execute(select_emp, {'emp_id':int(emp_id)})
        count = cursor.rowcount

        if count ==0:
            return "No matching employee id"

        for x in cursor:
            (emp_id,name,department)=x

        print(emp_id)
        cursor.execute("DELETE FROM seminar WHERE emp_id='"+emp_id+"'")
        db_conn.commit()
        cursor.close()
    return render_template('withdrawSuccess.html',name=name)


@app.route("/searchEmp", methods=['GET','POST'])
def SearchEmp():

    emp_id = request.form['emp_id']

    select_emp = "SELECT * FROM employee WHERE emp_id = %(emp_id)s"
    cursor = db_conn.cursor()

    filename = "emp-id-" + str(emp_id) + "_image_file"
    url = "https://%s.s3.amazonaws.com/%s" % (custombucket,filename)

    if emp_id == "":
        return "Please enter employee id"

    try:
        cursor.execute(select_emp, {'emp_id':int(emp_id)})
        count = cursor.rowcount

        if count ==0:
            return "No matching employee id"

        for x in cursor:
            (employee_id,first_name,last_name,department,job_title,pri_skill,location,salary)=x

    except Exception as e:
            return str(e)

    finally:
        cursor.close()
    return render_template('GetEmpOutput.html',id=employee_id,fname=first_name,lname=last_name,department=department,job_title=job_title,pri_skill=pri_skill,location=location,salary=salary,image_url=url)

@app.route("/edit", methods=['GET', 'POST'])
def editEmp():
    emp_id = request.args['emp_id']
    select_emp = "SELECT * FROM employee WHERE emp_id = %(emp_id)s"
    cursor = db_conn.cursor()

    filename = "emp-id-" + str(emp_id) + "_image_file"
    url = "https://%s.s3.amazonaws.com/%s" % (custombucket,filename)

    try:
        cursor.execute(select_emp, {'emp_id':int(emp_id)})
        count = cursor.rowcount

        if count ==0:
            return "No matching employee id"

        for x in cursor:
            (employee_id,first_name,last_name,department,job_title,pri_skill,location,salary)=x

    except Exception as e:
            return str(e)

    finally:
        cursor.close()
    return render_template('edit.html',id=employee_id,fname=first_name,lname=last_name,image_url=url)

@app.route("/edited", methods=['GET', 'POST'])
def editSuccess():
    emp_id = request.form['emp_id']
    department = request.form['department']
    job_title = request.form['job_title']
    pri_skill = request.form['pri_skill']
    location = request.form['location']
    salary = request.form['salary']
    emp_cert_file = request.files['emp_cert_file']
   
    update_sql = "UPDATE employee SET department = %s, job_title = %s, pri_skill = %s, location = %s, salary =%s WHERE emp_id = %s"
    cursor = db_conn.cursor()
    cursor.execute(update_sql, (department,job_title,pri_skill,location,salary,emp_id))
    db_conn.commit()
    cursor.close()

    emp_cert_file_name_in_s3 = "emp-id-" + str(emp_id) + "_cert_file"
    s3 = boto3.resource('s3')

    try:
            print("Data inserted in MySQL RDS... uploading image to S3...")
            s3.Bucket(custombucket).put_object(Key=emp_cert_file_name_in_s3, Body=emp_cert_file)
            bucket_location = boto3.client('s3').get_bucket_location(Bucket=custombucket)
            s3_location = (bucket_location['LocationConstraint'])

            if s3_location is None:
                s3_location = ''
            else:
                s3_location = '-' + s3_location

            object_url = "https://s3{0}.amazonaws.com/{1}/{2}".format(
                s3_location,
                custombucket,
                emp_cert_file_name_in_s3)

    except Exception as e:
            return str(e)

    return render_template('editSuccess.html')

@app.route("/viewCert", methods=['GET', 'POST'])
def viewCert():
    emp_id = request.form['cert_id']
    filename = "emp-id-" + str(emp_id) + "_cert_file"
    url = "https://%s.s3.amazonaws.com/%s" % (custombucket,filename)
    return render_template('viewCert.html',cert_url=url)    

@app.route("/attendance", methods=['GET', 'POST'])
def attendancemanagement():
    return render_template('attendancesystem.html')

@app.route("/clock", methods=['GET', 'POST'])
def Clock():
    return render_template('attendance.html')


@app.route("/leave", methods=['GET', 'POST'])
def applyleave():
    return render_template('leavemanagement.html')

@app.route("/applyleave", methods=['GET', 'POST'])
def applyleaveform():
    return render_template('ApplyLeave.html')

@app.route("/training", methods=['GET', 'POST'])
def Training():
    return render_template('training.html')

@app.route("/expired", methods=['GET', 'POST'])
def expired():
    return "No longer receiving response."

@app.route("/submitLeave", methods=['GET','POST'])
def submitLeave():
    emp_id = request.form['emp_id']
    name = request.form['name']
    department = request.form['department']
    leavetype = request.form['leave_type']
    startdate = request.form[ 'start_date']
    enddate = request.form['end_date']
    insert_sql = "INSERT INTO employee.leave VALUES (%s, %s, %s,%s,%s,%s,%s)"
    cursor = db_conn.cursor()
    try:

        cursor.execute(insert_sql, (name,emp_id,department,leavetype,startdate,enddate,"Pending"))
        db_conn.commit()
    finally:
        cursor.close()
    return render_template('applySuccess.html')

@app.route("/addemp", methods=['GET','POST'])
def AddEmp():
    emp_id = request.form['emp_id']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    department = request.form['department']
    job_title = request.form['job_title']
    pri_skill = request.form['pri_skill']
    location = request.form['location']
    salary = request.form['salary']
    emp_image_file = request.files['emp_image_file']

    insert_sql = "INSERT INTO employee VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
    cursor = db_conn.cursor()

    if emp_image_file.filename == "":
        return "Please select a file"

    try:

        cursor.execute(insert_sql, (emp_id, first_name, last_name, department, job_title, pri_skill, location, salary))
        db_conn.commit()
        emp_name = "" + first_name + " " + last_name
        # Uplaod image file in S3 #
        emp_image_file_name_in_s3 = "emp-id-" + str(emp_id) + "_image_file"
        s3 = boto3.resource('s3')

        try:
            print("Data inserted in MySQL RDS... uploading image to S3...")
            s3.Bucket(custombucket).put_object(Key=emp_image_file_name_in_s3, Body=emp_image_file)
            bucket_location = boto3.client('s3').get_bucket_location(Bucket=custombucket)
            s3_location = (bucket_location['LocationConstraint'])

            if s3_location is None:
                s3_location = ''
            else:
                s3_location = '-' + s3_location

            object_url = "https://s3{0}.amazonaws.com/{1}/{2}".format(
                s3_location,
                custombucket,
                emp_image_file_name_in_s3)

        except Exception as e:
            return str(e)

    finally:
        cursor.close()

    print("all modification done...")
    return render_template('AddEmpOutput.html', name=emp_name)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)

