from application import *
import numpy as np
from flask import send_file,redirect
import matplotlib.pyplot as plt

tracker_types = ['Numerical', 'Multiple Choice', 'Boolean', 'Time Duration']
bools = {'true':'True', 'false':'False', '0':'False', '1':'True'}

login=LoginManager(app)

def valid_username(uname):
    if uname.isalnum():
        return True
    else:
        return False

@login.user_loader
def load_user(uid):
    return Users.query.filter_by(uid=uid).first()


@app.route('/', methods = ['GET', 'POST'])
def user_login():
    if request.method == 'GET':
        return render_template("index.html")
    elif request.method == 'POST':
        uname = request.form.get("uname")
        if valid_username(uname):
            user = Users.query.filter_by(uname=uname).first()
            if user:
                if bcrypt.check_password_hash(user.password,request.form.get('password')):
                    login_user(user,False,None,True)
                    return redirect(f"/user/{uname}/home")
                else:
                    error = "Your Password Is Wrong"
                    raise InputError(400, "USER002", error_message=error, html_page="index.html")
            else:
                error = "Username Not Found"
                raise InputError(404, "USER001", error_message=error, html_page="index.html")
        else:
            error = "Invalid Username. It must be alpha-numerical"
            return render_template("index.html", error=error)

@app.route("/user/create", methods=['GET', 'POST'])
def user_create():
    if request.method == 'GET':
        return render_template("newuser.html")
    else: 
        uname_ = request.form.get("uname")
        hashedPassword = bcrypt.generate_password_hash(request.form.get("password"))
        old_user = Users.query.filter_by(uname=uname_).first()
        if uname_ and valid_username(uname_):
            user = Users(uname=uname_, password=hashedPassword)
            try:
                db.session.add(user)
                db.session.commit()
                flash("account created")
                return redirect("/")
            except:
                db.session.rollback()
                if old_user:
                    error = "Username already exists"
                    raise InputError(400, "USER003", error_message=error, html_page="newuser.html")
                error = "Server Error. Try again"
                raise InputError(500, "USER004", error_message=error, html_page="newuser.html")
        else:
            error = "Username invalid or empty. Username must be alpha-numerical"
            raise InputError(400, "USER005", error_message=error, html_page="newuser.html")


@app.route("/user/logout")
@login_required
def user_logout():
    logout_user()
    return redirect("/")


@app.route("/user/<uname>/home")
@login_required
def user_home(uname):
    uid = current_user.uid
    enrolls = Enrollments.query.filter_by(uid=uid).all()
    trackers = []
    logs = {}
    for e in enrolls:
        log = Logs.query.filter_by(uid=uid, trid=e.trid).order_by(Logs.lid.desc()).first()
        tracker = Trackers.query.filter_by(trid=e.trid).one()
        trackers.append(tracker)
        if log:
            logs[e.trid] = log.timestamp,log.value
        else:
            logs[e.trid] = None
        
    condition = False
    if trackers:
        condition = True
    
    f=0
    tracker = Trackers()
    loge = Logs.query.filter_by(uid=uid).order_by(Logs.lid.desc()).all()
    condition2 = False
    if loge:
        i = 0
        log = []
        while i < 3 and i < len(loge):
            log.append(loge[i])
            i += 1
        condition2 = True
        f=1
    if(f==0):
       return render_template("userhome.html", uname=uname, trackers=trackers, condition2=condition2, condition=condition, logs=logs)
    else: 
       return render_template("userhome.html", uname=uname, trackers=trackers, condition2=condition2, condition=condition, logs=logs, tracker=tracker, log=log )


@app.route("/user/<uname>/trackers/add", methods=['GET', 'POST']) 
@login_required
def tracker_create(uname):
    global tracker_types
    if request.method=="GET":
        return render_template("useraddtracker.html", uname=current_user.uname)
    elif request.method=='POST':
        new_tracker_name = request.form.get("trname")
        if not valid_username(new_tracker_name):
            error="Invalid name"
            raise InputError(400, "TRACKER004", html_page="useraddtracker.html", error_message=error, uname=current_user.uname)
        new_tracker_type = request.form.get("trtype")
        if new_tracker_type not in tracker_types:
            error = 'Tracker Not Valid'
            raise InputError(400, "TRACKER005", error, html_page="useraddtracker.html", uname=current_user.uname)
        
        new_tracerk_desc = request.form.get("trackerDesc")
        user = Users.query.filter_by(uname=uname).one()
        uid = user.uid
        new_tracker = Trackers(trname=new_tracker_name, trtype=new_tracker_type, trdesc=new_tracerk_desc)
        try:
            db.session.add(new_tracker)
            db.session.commit()
            tracker = Trackers.query.filter_by(trname = new_tracker_name).one()
            trid=tracker.trid
            new_enroll = Enrollments(uid=uid, trid=trid)
            db.session.add(new_enroll)
            db.session.commit()
            if new_tracker_type == "Multiple Choice":
                return redirect(f"/user/{uname}/{tracker.trid}/addselectables")
            try:
                db.session.add(new_enroll)
                db.session.commit()
                return redirect(f"/user/{uname}/home")
            except:
                db.session.rollback()
                error = "<h1>SERVER ERROR</h1>"
                raise ServerError(500, "USER006", error)                
        except:
            db.session.rollback()
            error = "Invalid Inputs"
            raise InputError(400, "TRACKER006", error, "useraddtracker.html", username=current_user.username)


@app.route("/user/<uname>/<int:trid>/addselectables", methods=['GET', 'POST'])
def tracker_selectablesua(uname,trid):
    if request.method == 'GET':
        tracker = Trackers.query.filter_by(trid = trid).one()
        return render_template("add_selectablesu.html", tracker=tracker, uname=uname, trid=trid)
    elif request.method == 'POST':
        new_choices = request.form.get("trackerChoices")
        new_selectables = Selectables(choices=new_choices,trid=trid)
        try:
            db.session.add(new_selectables)
            db.session.commit()
            return redirect(f"/user/{uname}/home")
        except:
            db.session.rollback()
            raise ServerError(500, "TRACKER007", "<h1>Server Error</h1>")


@app.route("/user/<uname>/<int:trid>/delete") 
@login_required
def user_tracker_del(uname, trid):
    enrolls = Enrollments.query.filter_by(uid=current_user.uid, trid=trid).all()
    logs = Logs.query.filter_by(uid=current_user.uid, trid=trid).all()
    tracker = Trackers.query.filter_by(trid=trid).one()
    try:
        for e in enrolls:
            db.session.delete(e)
        for log in logs:
            db.session.delete(log)
        db.session.delete(tracker)    
        db.session.commit()
        return redirect(f"/user/{uname}/home")
    except:
        db.session.rollback()
        error = "<h1>SERVER ERROR</h1>"
        raise ServerError(500, "USER006", error)


@app.route("/user/<uname>/<int:trid>/edit", methods=['GET', 'POST'])
@login_required
def user_tracker_edit(uname,trid):
    if request.method == 'GET':
        tracker = Trackers.query.filter_by(trid=trid).one()
        selectable_values = None
        if tracker.trtype == "Multiple Choice":
            try:
                selectable_values = Selectables.query.filter_by(trid=trid).one()
            except:
                pass
        return render_template("useredittracker.html", tracker=tracker, selectable_values = selectable_values, uname=current_user.uname, trid=trid)
    elif request.method == 'POST':
        new_name = request.form['trname']
        new_desc = request.form['trdesc']
        tracker = Trackers.query.filter_by(trid=trid).one()
        if valid_username(new_name):
            tracker.trname = new_name
            tracker.trdesc = new_desc
            try:
                db.session.commit()
                return redirect(f"/user/{uname}/home")
            except:
                db.session.rollback()
                error = "<h1>Could not edit tracker. SERVER ERROR </h1>"
                raise ServerError(500, "TRACKER001", error)
        else:
            error = "Invalid Name"
            raise InputError(400, "TRACKER002", html_page="tracker_edit.html", error_message=error, tracker=tracker, uname=current_user.uname)


@app.route("/user/<uname>/<int:trid>/editselectables", methods=['GET', 'POST'])
def tracker_selectablesue(uname,trid):
    if request.method == 'GET':
        tracker = Trackers.query.filter_by(trid = trid).one()
        return render_template("edit_selectablesu.html", tracker=tracker, uname=uname, trid=trid)
    elif request.method == 'POST':
        choices = request.form.get("trackerChoices")
        selectable_values = Selectables(trid=trid,choices=choices)
        try:
            logs = Logs.query.filter_by(trid=trid).all()
            selectables = Selectables.query.filter_by(trid=trid).one()
            for l in logs:
                db.session.delete(l)
            db.session.delete(selectables)
            db.session.commit()
        except:
            db.session.rollback()
            pass
        try:
            db.session.add(selectable_values)
            db.session.commit()
            return redirect(f"/user/{uname}/home")
        except:
            db.session.rollback()
            raise ServerError(500, "TRACKER007", "<h1>Server Error</h1>")


@app.route("/user/<uname>/<int:trid>/addlogs", methods=['GET', 'POST'])
@login_required
def user_tracker_log_add(uname, trid):
    if request.method=='GET':
        current = datetime.now()
        current = current.strftime("%d/%m/%Y %I:%M %p")
        tracker = Trackers.query.filter_by(trid=trid).first()
        if tracker.trtype == "Multiple Choice":
            s = Selectables.query.filter_by(trid=trid).first()
            choices = s.choices.split(",") 
            return render_template("useraddlog.html", uname=current_user.uname, tracker=tracker, current=current, condition=False, choices=choices)
        return render_template("useraddlog.html", uname=current_user.uname, tracker=tracker, current=current, condition=True)
    elif request.method=='POST':
        current = datetime.now()
        current = current.strftime("%d/%m/%Y %I:%M %p")
        value = request.form.get('value')
        tracker = Trackers.query.filter_by(trid=trid).first()
        if tracker.trtype == "Boolean":
            if value.lower() in bools:
                value = bools[value.lower()]
            else:
                error = "Boolean value is not allowed. Try 'true or false' or '1 or 0'"
                raise InputError(400, "LOG002", error, "useraddlog.html", tracker=tracker, uname=current_user.uname, condition=True, current=current)
        elif tracker.trtype == "Numerical" or tracker.trtype == "Time Duration":
            value = float(value)
        elif tracker.trtype == "Multiple Choice":
            pass    
        elif type(value) not in tracker_types:
            error = "Your value doesn't match the tracker type"
            if tracker.trtype == "Multiple Choice":
                s = Selectables.query.filter_by(trid=trid).first()
                choices = s.choices.split(",")
                raise InputError(400, "LOG001", error, "useraddlog.html", uname=current_user.uname, tracker=tracker, current=current, condition=False, choices=choices)
            raise InputError(400, "LOG002", error, "useraddlog.html", tracker=tracker, uname=current_user.uname, condition=True, current=current)
        note = request.form.get('note')
        timestamp = request.form.get('datetime')
        log = Logs(value=value, note=note, timestamp=timestamp, trid=trid, uid=current_user.uid)
        try:
            db.session.add(log)
            db.session.commit()
            return redirect(f"/user/{uname}/home")
        except:
            db.session.rollback()
            raise ServerError(500, "LOG003", "<h1>SERVER ERROR</h1>")
