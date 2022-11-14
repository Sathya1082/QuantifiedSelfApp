from application import *
from flask import send_file
from matplotlib import pyplot as plt
import numpy as np


def valid_name(name):
    if name.isalnum():
        return True
    else:
        return False

bools = {'true':'True', 'false':'False', '0':'False', '1':'True'}
tracker_types = {'Numerical': float, 'Multiple Choice': str, 'Boolean': str, 'Time Duration': float}

 
@app.route("/user/<uname>/<int:trid>/tracker_info") 
@login_required
def tracker_info(uname,trid):
    logs = Logs.query.filter_by(trid=trid, uid=current_user.uid).all()
    tracker = Trackers.query.filter_by(trid=trid).first()
    s = None
    if (tracker.trtype == "Multiple Choice"):
        choices = Selectables.query.filter_by(trid=trid).first()
        s = choices.choices
        condition = True
    elif (tracker.trtype == "Numerical" or tracker.trtype == "Time Duration" or tracker.trtype=="Boolean") and logs:
        condition = True
    elif logs:
        condition=False
       
    return render_template("tracker_info.html", uname=uname, tracker=tracker, condition=condition, logs=logs, s=s)

@app.route("/user/<uname>/plot_png/<int:trid>")
@login_required
def plot_png(uname,trid):
    tracker = Trackers.query.filter_by(trid=trid).one()
    if tracker.trtype != "Multiple Choice" and tracker.trtype != "Boolean":
        logs = Logs.query.filter_by(trid=trid, uid=current_user.uid).all()
        tracker = Trackers.query.filter_by(trid=trid).first()
        timestamps = []
        values = []
        for log in logs:
            timestamps.append(log.timestamp)
            values.append(float(log.value))

        timestamps = np.array(timestamps)
        values = np.array(values)
        timestamps.sort() 
        values.sort()
    
        if tracker.trtype == "Numerical":
            plt.plot(values,timestamps)
            plt.xlabel("Value")
            plt.tight_layout()
            plt.yticks(rotation=45, ha='right')
            plt.savefig("output.png")
        elif tracker.trtype == "Time Duration":
            plt.bar(timestamps, values)
            plt.xticks(rotation=90, ha='right')
            plt.tight_layout()
            plt.ylabel("Value")
            plt.savefig("output.png",bbox_inches ="tight",pad_inches = 1,transparent = True, facecolor ="g",edgecolor ='w',orientation ='landscape')
        plt.close()
    
        return send_file("../output.png", mimetype="image/png")

@app.route("/user/<uname>/tracker_info/<int:trid>/edit", methods=['GET', 'POST'])
@login_required
def tracker_editt(uname,trid):
    if request.method == 'GET':
        tracker = Trackers.query.filter_by(trid=trid).one()
        selectable_values = None
        if tracker.trtype == "Multiple Choice":
            try:
                selectable_values = Selectables.query.filter_by(trid=trid).one()
            except: 
                pass
        return render_template("trackeredittracker.html", tracker=tracker, selectable_values = selectable_values, uname=current_user.uname, trid=trid)
    elif request.method == 'POST':
        new_name = request.form['trackerName']
        new_desc = request.form['trackerDesc']
        tracker = Trackers.query.filter_by(trid=trid).one()
        if valid_name(new_name):
            tracker.trname = new_name
            tracker.trdesc = new_desc
            try:
                db.session.commit()
                return redirect(f"/user/{uname}/{trid}/tracker_info")
            except:
                db.session.rollback()
                error = "<h1>Could not edit tracker. SERVER ERROR </h1>"
                raise ServerError(500, "TRACKER001", error)
        else:
            error = "Invalid Name"
            raise InputError(400, "TRACKER002", html_page="trackeredittracker.html", error_message=error, tracker=tracker, username=current_user.username)


@app.route("/user/<uname>/tracker_info/<int:trid>/editselectables", methods=['GET', 'POST'])
def tracker_selectables(uname,trid):
    if request.method == 'GET':
        tracker = Trackers.query.filter_by(trid = trid).one()
        return render_template("edit_selectablest.html", tracker=tracker)
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
            return redirect(f"/user/{uname}/{trid}/tracker_info")
        except:
            db.session.rollback()
            raise ServerError(500, "TRACKER007", "<h1>Server Error</h1>")


@app.route("/user/<uname>/tracker_info/<int:trid>/delete")
@login_required
def tracker_delt(uname,trid):
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
    