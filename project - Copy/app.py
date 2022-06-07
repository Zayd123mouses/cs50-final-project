import os
import json

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session,send_file
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import timedelta
from helper import apology, login_required
from datetime import datetime, date
import os
import csv
import random
from flask_mail import Mail, Message
import smtplib
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()
# Configure application
app = Flask(__name__)
now = datetime.now()
time = now.strftime("%d/%m/%Y %H:%M:%S")
d3 = now.strftime("%Y-%m-%d")
# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

#flask-mail config

# Configure session to use filesystem (instead of signed cookies)
app.config['PERMANENT_SESSION_LIFETIME'] =  timedelta(minutes=5)
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///data.db")
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = os.getenv('EMAIL')
app.config['MAIL_PASSWORD'] = os.getenv('PASS')
app.config['MAIL_USE_TLS'] = True
mail = Mail(app)





@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

def updating(id):
    db.execute("UPDATE details SET answer = 'outdated' , this_session = 'outdated' WHERE id = ? AND date < ? AND answer = 'confirmed' AND this_session IS NULL",id,d3)

def inject():
    data = db.execute("SELECT email FROM patients WHERE email = ?",session["email"])
    if data:
         return "p"
    else:
        return'd'



@app.route("/")
@login_required
def index():
    # ensure what type of user is trying to enter
    if inject() == 'p':
        return redirect("/patients")

    else:
        return render_template("index.html")


@app.route("/requests", methods=["POST","GET"])
@login_required
def requests():
    if request.method == "POST":
        yes =request.form.get("yes")
        time = request.form.get("time")
        date = request.form.get("date")
        p_id = request.form.get("p_id")
        doctor = db.execute("SELECT name FROM users WHERE id = ?", session["user_id"])

        if request.form["button"] == 'no':
            db.execute("UPDATE  details set answer = 'false' WHERE TIME = ? AND date = ? AND p_id = ? AND id = ?",time,date,p_id,session["user_id"])
            doctor = db.execute("SELECT name FROM users WHERE id = ?", session["user_id"])
            msg = Message('Hello from the other side!', sender = os.getenv("EMAIL"), recipients = [request.form.get("email")])
            msg.body = f"hey, your doctor {doctor[0]['name']}ID {session['user_id'] } has declined  your apointment request due to urgent matter!!!"
            mail.send(msg)

            return redirect("/requests")

        elif request.form["button"] == 'yes':
            taken = db.execute("SELECT p_id FROM details WHERE TIME = ? AND date = ? AND p_id = ? AND id = ? AND answer = 'confirmed' AND this_session IS NULL", time,date,p_id,session["user_id"])
            if taken:
                flash("You have apointment at that time")
                return redirect("/requests")

            time_differ = db.execute("SELECT TIME FROM details WHERE date = ? AND id = ? AND answer = 'confirmed' AND this_session IS NULL",date,session["user_id"])
            index = 0
            while index < len(time_differ):
                for key in time_differ[index]:
                    time_differ[index][key] = time_differ[index][key].replace(":", ".")
                    if float(time_differ[index][key]) < 1 or float(time_differ[index][key]) > -1:
                        flash("this time is OCCUPIED please choose another time")
                        session["patient"] = request.form.get("p_id")
                        return redirect("/times")
                index += 1



            db.execute("UPDATE details SET gender = (SELECT gender FROM details WHERE p_id = ? AND this_session = 'done') WHERE p_id = ?",p_id,p_id)
            db.execute("UPDATE details SET answer ='confirmed' WHERE TIME = ? AND date = ? AND p_id = ? AND id = ?",time,date,p_id,session["user_id"])
            msg = Message('Hello from the other side!', sender = os.getenv("EMAIL"), recipients = [request.form.get("email")])
            msg.body = f"hey, your doctor{doctor[0]['name']} ID {session['user_id'] } has accepted  your apointment request you can view it in your apointment page!!!"
            mail.send(msg)
            return redirect("/requests")
        else:
            session["patient"] = request.form.get("p_id")
            return redirect("/times")

    else:
        if inject() == 'p':
                return redirect("/patients")
        db.execute("UPDATE details SET answer = 'outdated' , this_session = 'outdated' WHERE id = ? AND date < ? AND answer IS NULL AND this_session IS NULL",session["user_id"],d3)
        data = db.execute("SELECT * FROM patients JOIN details ON details.p_id = patients.p_id WHERE patients.p_id IN (SELECT p_id FROM details WHERE id = ? ) AND answer IS NULL",session["user_id"])
        numbers = db.execute("SELECT COUNT(p_id) AS number FROM details WHERE id = ? AND answer IS NULL",session["user_id"])
        flash("You can check the patients medical record in the patient details page before accepting the apointment")
        return render_template("requests.html",data=data,data2=int(numbers[0]['number']))


@app.route("/myday", methods=["POST","GET"])
@login_required
def myday():
    if request.method == 'POST':
        if request.form["button"] == 'cancel':
            db.execute("UPDATE details SET answer = ? WHERE p_id = ? AND this_session IS NULL AND id = ? AND TIME = ?",'canceled',request.form.get("id"),session["user_id"],request.form.get("hour"))

            msg = Message('About your apointment', sender = os.getenv("EMAIL"), recipients = [request.form.get("email")])
            msg.body = f"We appologize that your doctor has canceled the apointment that was at {request.form.get('time')} due to urgent reason, thanks for your understanding"
            mail.send(msg)
            return redirect("/myday")

        elif request.form["button"] == 'edit':


            session["patient"] = request.form.get("id")

            return redirect("/times")

        else:

            session["to_email"] = request.form.get("email")
            return redirect("/emails")

    else:
        if inject() == 'p':
                return redirect("/patients")
        updating(session["user_id"])
        data2 = db.execute("SELECT date FROM details WHERE id = ? AND answer = 'confirmed' AND this_session IS NULL",session["user_id"])

        data = db.execute("SELECT details.p_id AS p_id, patients.name, details.age, details.gender ,statue, date, TIME, patients.email, users.name AS doctor FROM details JOIN patients JOIN users  ON details.p_id = patients.p_id AND details.id =  users.id WHERE users.id = ? AND this_session IS NULL AND answer='confirmed'",session["user_id"])
        return render_template("myday.html",data=data,data2=data2)


@app.route("/diagnosis", methods=["POST","GET"])
@login_required
def diagnosis():
    if request.method == "POST":
        #turn the list of strings into a full string
        on = request.form.getlist("inp")
        signs = ','.join(on)
        medss = request.form.get("medss")
        p_id = request.form.get("mylist")
        dises = request.form.get('recommed')
        meds = request.form.get('meds')
        emails = db.execute('SELECT email,name,p_id FROM patients WHERE p_id = ?',p_id)

        db.execute("UPDATE details SET this_session = 'done', gender = coalesce(?, gender), symptoms = coalesce(?, symptoms), diagnosis =coalesce(?, diagnosis), treatment = coalesce(?, treatment), age = coalesce(?, age), note = coalesce(?, note), p_dis= coalesce(?, p_dis), meds = coalesce(?, meds), signs = ? WHERE id = ? AND p_id = ?",
        request.form.get('role'),request.form.get('symp'),request.form.get('diagnosis'),request.form.get('treatment'),request.form.get('age'),request.form.get('comment'), request.form.get('dis'), medss ,signs,session["user_id"],p_id)
        email(emails[0]['email'],emails[0]['p_id'],emails[0]['name'])
        flash("form has been submitted successfully")
        return redirect("/diagnosis")


    else:
        if inject() == '':
                return redirect("/patients")
        updating(session["user_id"])
        data = db.execute("SELECT * FROM patients JOIN details ON details.p_id = patients.p_id WHERE patients.p_id IN (SELECT p_id FROM details WHERE id = ? ) AND answer = 'confirmed' AND this_session IS NULL",session["user_id"])
        return render_template("diagnosis.html",data=data)

def email(email,id,name):
    msg = Message('Hello from the other side!', sender = os.getenv("EMAIL"), recipients = [email])
    msg.body = f"hey, your doctor {name} ID {id } has sent your diagnosis come check it out!!!"
    mail.send(msg)


@app.route("/update",  methods=["POST","GET"])
@login_required
def update():
    if request.method == 'POST':
        button = request.form["button"]

        if button == "yours":
            data = db.execute("SELECT *, patients.email AS p_email,patients.name AS p_name, details.p_id AS p_id FROM details JOIN patients ON patients.p_id = details.p_id WHERE details.p_id = ? AND details.id = ? AND this_session='done'",request.form.get("id"),session["user_id"])
            return render_template("yours.html",data=data)

        elif button == "previous":
            data = db.execute("SELECT *, patients.email AS p_email,patients.name AS p_name, users.name AS d_name,details.p_id AS p_id FROM details JOIN patients JOIN users ON patients.p_id = details.p_id AND  details.id = users.id WHERE details.p_id = ? AND this_session='done'",request.form.get("id"))
            return render_template("previous.html",data=data)

        elif button == 'edit':
            here = db.execute("SELECT p_id FROM details WHERE p_id = ? AND this_session = 'done'",request.form.get("id"))
            if not here:
                flash(f"You have not treated this patient before!.Please diagnose the patient first")
                return redirect("/update")
            session['p_time'] =  request.form.get("hour")
            return redirect("/edit")
        else:
            session["to_email"] = request.form.get("email")
            return redirect("/emails")



    else:
        if inject() == 'p':
                return redirect("/patients")
        data = db.execute("SELECT details.p_id, patients.name, details.age, details.gender ,statue, date, TIME, patients.email, users.name AS doctor FROM details JOIN patients JOIN users  ON details.p_id = patients.p_id AND details.id =  users.id WHERE users.id = ? AND statue = 'consult'",session["user_id"])
        return render_template("update.html",data=data)


@app.route('/yours', methods=["POST","GET"])
@login_required
def yours():
    if request.method == 'POST':
        if request.form["button"] == 'download':

            id = request.form.get("id")
            data = db.execute("SELECT patients.name AS Patient, details.p_id AS Pateint_ID, gender, time, date ,patients.email AS email, p_dis AS previous_disease ,meds AS current_medicin ,symptoms,signs,diagnosis,treatment,note AS Notes FROM details JOIN patients ON patients.p_id = details.p_id WHERE details.p_id = ? AND this_session = ? ",id,'done')
            keys = data[0].keys()
            with open('patients.csv', 'w', newline='') as output_file:
                dict_writer = csv.DictWriter(output_file, keys)
                dict_writer.writeheader()
                dict_writer.writerows(data)
            return send_file("patients.csv")
        else:
            session["to_email"] = request.form.get("email")
            return redirect("/emails")

    else:
        return "Access denied error 303"


@app.route('/previous', methods=["POST"])
@login_required
def previous():
    if request.form["button"] == 'download':

        data = db.execute("SELECT patients.name AS Patient, details.p_id AS Pateint_ID, gender, time, date ,patients.email AS email, p_dis AS previous_disease ,meds AS current_medicin ,symptoms,signs,diagnosis,treatment,note AS Notes,users.name AS Doctor_name FROM details JOIN patients JOIN users ON patients.p_id = details.p_id AND  details.id = users.id WHERE details.p_id = ? AND this_session='done'",request.form.get("id"))
        keys = data[0].keys()
        with open('previous.csv', 'w', newline='') as output_file:
            dict_writer = csv.DictWriter(output_file, keys)
            dict_writer.writeheader()
            dict_writer.writerows(data)
        return send_file("previous.csv")
    else:
        session["to_email"] = request.form.get("email")
        return redirect("/emails")



#to send emails on every contact button
@app.route('/emails', methods=["GET","POST"])
@login_required
def emails():
    if request.method == 'POST':
        msg = Message('A message FROM your doctor!', sender = os.getenv("EMAIL"), recipients = [session["to_email"]])
        msg.body = f"{request.form.get('msg')}"
        mail.send(msg)
        flash("Your email has been sent succefully")
        return render_template("emails.html")
    else:
        if inject() == 'p':
                return redirect("/patients")
        return render_template("emails.html",email=session["to_email"])

@app.route('/add', methods=["GET","POST"])
@login_required
def add():
    if request.method == 'POST':

        date = request.form.get("date")
        p_id = request.form.get("id")
        time = request.form.get("time")

        time_differ = db.execute("SELECT TIME FROM details WHERE date = ? AND id = ? AND answer = 'confirmed' AND this_session IS NULL",date,session["user_id"])
        index = 0
        while index < len(time_differ):
            for key in time_differ[index]:
                time_differ[index][key] = time_differ[index][key].replace(":", ".")
                if float(time_differ[index][key]) < 1 or float(time_differ[index][key]) > -1:
                    flash("An hour must be between every date please choose another houror another date")
                    session["patient"] = request.form.get("p_id")
                    return redirect("/times")
            index += 1
        taken = db.execute("SELECT * FROM details WHERE date = ? AND TIME = ? AND id = ? AND answer = 'confirmed' AND this_session IS NULL",date,time,session["user_id"])
        if taken:
            flash("This time is OCCUPIED Please choose another time")
            return redirect("/add")
        db.execute("INSERT INTO details (id,p_id,date,TIME,request,answer,statue) VALUES (?,?,?,?,'sent','confirmed','revisit')",session["user_id"],p_id,date,time)
        flash("A new appointment has been added successfully")
        return redirect("/add")



    else:
        if inject() == 'p':
                return redirect("/patients")

        data = db.execute("SELECT DISTINCT(p_id) FROM details WHERE this_session = 'done' AND p_id NOT IN(SELECT p_id FROM details WHERE this_session IS NULL and answer='confirmed') ")
        data2 = db.execute("SELECT p_id,date, TIME  FROM details WHERE this_session IS NULL and answer = 'confirmed'")
        return render_template("add.html", data=data,data2=data2)



@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()


    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        options = request.form["btnradio"]


        if options == "doc":
            rows = db.execute("SELECT * FROM users WHERE email = ?", request.form.get("email"))
            if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")) or rows[0]["name"] != request.form.get("username") or rows[0]["email"] != request.form.get("email"):
                flash("invalid username and/or password")
                return apology("login")

            session["user_id"] = rows[0]["id"]
            session["email"] = rows[0]["email"]
            session.permanent = True

            return redirect("/")

        else:

        # Query database for username
            rows = db.execute("SELECT * FROM patients WHERE email = ?", request.form.get("email"))


        # Ensure username exists and password is correct
            if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")) or rows[0]["name"] != request.form.get("username") or rows[0]["email"] != request.form.get("email"):
                flash("invalid username and/or password")
                return apology("login")


        # Remember which user has logged in
            session["user_id"] = rows[0]["p_id"]
            session["email"] = rows[0]["email"]
            session.permanent = True
        # Redirect user to home page
            return redirect("/patients")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":

        email = request.form.get("email")
        password = request.form.get("password")

        hash_pass = generate_password_hash(password)
        options = request.form["btnradio"]

        taken = db.execute("SELECT email FROM users WHERE email = ?",email)
        taken2 = db.execute("SELECT email FROM patients WHERE email = ?",email)

        if options == "doc":
            if taken or taken2:
                flash ("please choose another email")
                return render_template("register.html")

            db.execute("INSERT INTO users (name, email, hash,spec,exp) VALUES(?,?,?,?,?)",request.form.get("username"),email,hash_pass,request.form.get("yes").capitalize(),request.form.get("exp"))
            return redirect("/login")
        else:
            if taken2 or taken:
                flash ("please choose another email")
                return render_template("register.html")
            db.execute("INSERT INTO patients (name, email, hash) VALUES(?,?,?)",request.form.get("username"),email,hash_pass)
            return render_template("login.html")

    else:
        taken3 = db.execute("SELECT email FROM patients")
        return render_template("register.html",taken=taken3)

@app.route("/logout")
def logout():

    session.clear()
    return redirect("/login")


@app.route("/patients")
@login_required
def patients():
    if inject() == 'd':
                return redirect("/")
    else:
        return render_template("index2.html")



@app.route("/body")
@login_required
def body():
        if inject() == 'd':
                return redirect("/")
        return render_template("body.html")

@app.route("/burned")
@login_required
def burned():
        if inject() == 'd':
                return redirect("/")
        return render_template("burned.html")



@app.route("/bookapoint", methods=["POST","GET"])
@login_required
def book():
    if request.method =="POST":
        if request.form.get("button"):
            print('doctor ID: ', request.form.get('button'))
        id = request.form.get("id")
        time = request.form.get("time")
        dates = request.form.get("date")

        spam = db.execute("SELECT request FROM details WHERE TIME = ? AND p_id = ? AND id = ? AND date = ? AND this_session IS NULL",time,session["user_id"],id,dates)
        if spam:
            flash("you have an apointment at this time with that doctor")
            return redirect("/bookapoint")

        max = db.execute("SELECT COUNT(p_id) AS max FROM details WHERE p_id = ? AND id = ? AND answer IS NULL",session["user_id"],id)
        if max[0]["max"] >= 1:
            flash("You have an appointment request waiting to be answered by the doctor")
            return redirect("/bookapoint")

        already = db.execute("SELECT COUNT(p_id) AS already FROM details WHERE P_id = ? and answer IS NULL",session["user_id"])
        if already[0]['already'] >= 1:
            flash("You have a request with another doctor waiting to be accepted by the doctor")
            return redirect("/bookapoint")


        revist = db.execute("SELECT p_id FROM details WHERE p_id = ? AND id = ? AND this_session = 'done'",session["user_id"],id)
        if revist:
            db.execute("INSERT INTO details (id,p_id,request,time,date,statue) VALUES(?,?,'sent',?,?,'revisit')",id,session["user_id"],str(time),str(dates))
            flash("Request has been sent to the docotr.")
            return redirect("/bookapoint")

        busy = db.execute("SELECT id FROM details WHERE id = ? AND date = ? AND TIME = ? AND answer = ?",id,dates,time,'confirmed')
        if busy:
            flash("The doctor has an apointment at this time , please choose another apointment")
            return redirect("/bookapoint")


        else:
           db.execute("INSERT INTO details (id,p_id,request,time,date,statue) VALUES(?,?,'sent',?,?,'consult')",id,session["user_id"],str(time),str(dates))
           flash("Request has been sent to the docotr AND waiting for the doctor response")
           return redirect("/bookapoint")

    else:
        if inject() == 'd':
                return redirect("/")
        data = db.execute("SELECT * FROM users GROUP BY spec")
        data2 = db.execute("SELECT * FROM users")
        return render_template("apointment.html",data=data,data2=data2,d3=d3)



@app.route('/edit',  methods=["POST","GET"])
@login_required
def edit():
    if request.form == "POST":
        on = request.form.getlist("inp")
        signs = ','.join(on)
        p_id = request.form.get("mylist")
        db.execute("UPDATE details SET this_session = 'done', gender = coalesce(?, gender), symptoms = coalesce(?, symptoms), diagnosis =coalesce(?, diagnosis), treatment = coalesce(?, treatment), age =coalesce(?, age), note = coalesce(?, note), p_dis=coalesce(?, p_dis), meds = coalesce(?, meds), signs = ? WHERE id = ? AND p_id = ? AND date = ?",
            request.form.get('role'),request.form.get('symp'),request.form.get('diagnosis'),request.form.get('treatment'),int(request.form.get('age')),request.form.get('comment'),request.form.get('dis'),request.form.get("medss"),signs,session["user_id"],p_id,session["p_time"])
        return redirect("/update")
    else:
        if inject() == 'p':
                return redirect("/patients")
        data = db.execute("SELECT * FROM patients JOIN details ON details.p_id = patients.p_id WHERE patients.p_id IN (SELECT p_id FROM details WHERE id = ? ) AND answer = 'confirmed' AND this_session = 'done'",session["user_id"])
        return render_template("edit.html",data=data)



@app.route('/p_apointments',  methods=["POST","GET"])
@login_required
def p_apointments():
    if request.method == 'POST':
        session["to_email"] = request.form.get("email")
        return redirect("/emails2")


    else:
        if inject() == 'd':
                return redirect("/")

        db.execute("UPDATE details SET answer = 'outdated' , this_session = 'outdated' WHERE p_id = ? AND date < ? AND answer = 'confirmed' AND this_session IS NULL",session["user_id"],d3)
        data2 = db.execute("SELECT date FROM details WHERE p_id = ? AND answer = 'confirmed' AND this_session IS NULL",session["user_id"])
        data = db.execute("SELECT details.p_id, patients.name, details.age, details.gender ,statue, date, TIME, patients.email, users.name AS doctor, users.email AS d_email, users.id AS d_id FROM details JOIN patients JOIN users  ON details.p_id = patients.p_id AND details.id =  users.id WHERE details.p_id = ? AND this_session IS NULL AND answer='confirmed'",session["user_id"])
        return render_template("p_apointments.html",data=data,data2=data2)

@app.route('/history', methods=["POST","GET"])
@login_required
def history():
    if request.method == 'POST':
        if request.form["button"] == 'd_email':
            session["to_email"] = request.form.get("d_email")
            return redirect("/emails")
        else:
            session["to_email"] = request.form.get("p_email")
            return redirect("/emails")


    else:
        if inject() == 'd':
                return redirect("/")
        data = db.execute("SELECT *, patients.email AS p_email,patients.name AS p_name, users.name AS d_name, users.email AS d_email FROM details JOIN patients JOIN users ON patients.p_id = details.p_id AND  details.id = users.id WHERE details.p_id = ? AND this_session='done'",session["user_id"])
        return render_template("history.html",data=data)



#due to html layout problem i made another one for patiennts
@app.route('/emails2', methods=["GET","POST"])
@login_required
def emails2():
    if request.method == 'POST':
        msg = Message('A message FROM your doctor!', sender = os.getenv("EMAIL"), recipients = [session["to_email"]])
        msg.body = f"{request.form.get('msg')}"
        mail.send(msg)
        flash("Your email has been sent succefully")
        return render_template("emails2.html")


    else:
        if inject() == 'd':
                return redirect("/")
        return render_template("emails2.html",email=session["to_email"])



@app.route('/times', methods=["GET","POST"])
@login_required
def times():
    if request.method == 'POST':

        check = db.execute("SELECT date, TIME FROM details WHERE p_id = ? AND id = ? AND this_session IS NULL and answer = ? AND TIME = ? AND date = ?",request.form.get("mylist"),session["user_id"], 'confirmed',request.form.get("time"), request.form.get("date"))
        if check:
            flash("You have an apointment at that time")
            return redirect("/times")

        time_differ = db.execute("SELECT TIME FROM details WHERE date = ? AND id = ? AND answer = 'confirmed' AND this_session IS NULL AND answer = 'confirmed'",request.form.get("date"),session["user_id"])
        index = 0
        while index < len(time_differ):
            for key in time_differ[index]:
                time_differ[index][key] = time_differ[index][key].replace(":", ".")
                if float(time_differ[index][key]) < 1 or float(time_differ[index][key]) > -1:
                    flash("this time is busy")
                    return redirect("/requests")
            index += 1
        else:
            db.execute("UPDATE details SET TIME = ? ,date = ?, answer = 'confirmed' WHERE p_id = ? AND id = ? AND this_session IS NULL and answer IS NULL ",request.form.get("time"), request.form.get("date"), request.form.get("mylist"),session["user_id"])
            flash("Update has been saved!!")
            return redirect("/times")



    else:
        if inject() == 'p':
                return redirect("/patients")
        data = db.execute("SELECT * FROM details WHERE id = ? AND this_session IS NULL and answer = ?",session["user_id"],'confirmed')
        return render_template("times.html", id = session["patient"],data=data, d3=d3)


@app.route('/forgot', methods=["GET","POST"])
def forgot():
    if request.method == 'POST':
        the_email = str(request.form.get("email"))

        try:
            role = request.form["btnradio"]
        except:
            button = request.form["button"]

        try:
            if role == 'doc':
                session["pass_reset"] = str(request.form.get("email"))
                exist = db.execute("SELECT email FROM users WHERE email = ?",str(request.form.get("email")))
                if not exist:
                    flash("This email has not been registred")
                    return redirect("/forgot")

           #random code to send via mail
                randomlist = []
                for i in range(0,5):
                    n = random.randint(1,100)
                    randomlist.append(n)
                string_ints = [str(int) for int in randomlist]
                str_of_ints = "".join(string_ints)

                here = db.execute("SELECT  email FROM codes WHERE email = ?",str(request.form.get("email")))
                if here:
                    db.execute("UPDATE codes SET code = ? WHERE email = ?",str_of_ints, str(request.form.get("email")))
                else:
                    db.execute("INSERT INTO codes (code,email) VALUES(?,?) ",str_of_ints, str(request.form.get("email")))

                    msg = Message('Reset your password', sender = os.getenv("EMAIL"), recipients = [request.form.get("email")])
                    msg.body = f"Please enter this code in the website to reset your email {str_of_ints}"
                    mail.send(msg)
                    flash("A code has been sent succefully")
                    return render_template("reset_doc.html")


            elif role == "pate":
                session["pass_reset"] = str(request.form.get("email"))
                exist = db.execute("SELECT email FROM patients WHERE email = ?",str(request.form.get("email")))
                if not exist:
                    flash("This email has not been registred")
                    return redirect("/forgot")

           #random code to send via mail
                randomlist = []
                for i in range(0,5):
                    n = random.randint(1,100)
                    randomlist.append(n)
                string_ints = [str(int) for int in randomlist]
                str_of_ints = "".join(string_ints)

                here = db.execute("SELECT  email FROM codes WHERE email = ?",str(request.form.get("email")))
                if here:
                    db.execute("UPDATE codes SET code = ? WHERE email = ?",str_of_ints, str(request.form.get("email")))
                else:
                    db.execute("INSERT INTO codes (code,email) VALUES(?,?) ",str_of_ints, str(request.form.get("email")))

                    msg = Message('Reset your password', sender = os.getenv("EMAIL"), recipients = [request.form.get("email")])
                    msg.body = f"Please enter this code in the website to reset your email {str_of_ints}"
                    mail.send(msg)
                    flash("A code has been sent succefully")
                    return render_template("reset_pate.html")



        except:
            if request.form["button"] == 'code':

                the_code = db.execute("SELECT code FROM codes WHERE email = ?",session["pass_reset"])
                if not the_code:
                    flash("WRONG CODE PLEASE ENTER A VALID CODE")
                    return render_template("reset_doc.html")
                return render_template("new_password_doc.html")

            if request.form["button"] == 'password':
                password = request.form.get("password")
                hash_pass = generate_password_hash(password)
                db.execute("UPDATE users SET hash = ? WHERE email = ?",hash_pass,session["pass_reset"])
                flash("Password has been updated")
                return redirect("/login")

            elif request.form["button"] == 'code_pate' :
                the_code = db.execute("SELECT code FROM codes WHERE email = ?",session["pass_reset"])
                if not the_code:
                    flash("WRONG CODE PLEASE ENTER A VALID CODE")
                    return render_template("reset_doc.html")
                return render_template("new_password_pate.html")

            if request.form["button"] == 'password_pate':
                password = request.form.get("password")
                hash_pass = generate_password_hash(password)
                db.execute("UPDATE patients SET hash = ? WHERE email = ?",hash_pass,session["pass_reset"])
                flash("Password has been updated")
                return redirect("/login")

    else:
        return render_template("forgot.html")
