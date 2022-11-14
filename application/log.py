from application import *

bools = {'true':'True', 'false':'False', '0':'False', '1':'True'}
tracker_types = {'Numerical': float, 'Multiple Choice': str, 'Boolean': str, 'Time Duration': float}



@app.route("/user/<uname>/tracker_info/<int:trid>/addlogs", methods=['GET', 'POST'])
@login_required
def tracker_log_add(uname, trid):
    if request.method=='GET': 
        current = datetime.now()
        current = current.strftime("%d/%m/%Y %I:%M %p")
        tracker = Trackers.query.filter_by(trid=trid).first()
        if tracker.trtype == "Multiple Choice":
            s = Selectables.query.filter_by(trid=trid).first()
            choices = s.choices.split(",") 
            return render_template("trackeraddlog.html", uname=current_user.uname, tracker=tracker, current=current, condition=False, choices=choices)
        return render_template("trackeraddlog.html", uname=current_user.uname, tracker=tracker, current=current, condition=True)
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
                raise InputError(400, "LOG002", error, "trackeraddlog.html", tracker=tracker, uname=current_user.uname, condition=True, current=current)
        elif tracker.trtype == "Numerical" or tracker.trtype == "Time Duration":
            value = float(value)
        if type(value) != tracker_types[tracker.trtype]:
            error = "Your value doesn't match the tracker type"
            if tracker.trtype == "Multiple Choice":
                s = Selectables.query.filter_by(trid=trid).first()
                choices = s.choices.split(",")
                raise InputError(400, "LOG001", error, "trackeraddlog.html", uname=current_user.uname, tracker=tracker, current=current, condition=False, choices=choices)
            raise InputError(400, "LOG002", error, "trackeraddlog.html", tracker=tracker, uname=current_user.uname, condition=True, current=current)
        note = request.form.get('note')
        timestamp = request.form.get('datetime')
        log = Logs(value=value, note=note, timestamp=timestamp, trid=trid, uid=current_user.uid)
        try:
            db.session.add(log)
            db.session.commit()
            return redirect(f"/user/{uname}/{trid}/tracker_info")
        except:
            db.session.rollback()
            raise ServerError(500, "LOG003", "<h1>SERVER ERROR</h1>")



@app.route("/user/<uname>/<int:trid>/<int:lid>/editlogs", methods=['GET', 'POST'])
@login_required
def tracker_editlogs(uname,trid,lid):
    if request.method=='GET':
        current = datetime.now()
        current = current.strftime("%d/%m/%Y %I:%M %p")
        tracker = Trackers.query.filter_by(trid=trid).first()
        if tracker.trtype == "Multiple Choice":
            s = Selectables.query.filter_by(trid=trid).first()
            choices = s.choices.split(",") 
            return render_template("trackereditlog.html", uname=current_user.uname, tracker=tracker, current=current, condition=False, choices=choices,lid=lid)
        return render_template("trackereditlog.html", uname=current_user.uname, tracker=tracker, current=current, condition=True,lid=lid)
    elif request.method=='POST':
        current = datetime.now()
        current = current.strftime("%d/%m/%Y %I:%M %p")
        new_value = request.form.get('value')
        tracker = Trackers.query.filter_by(trid=trid).first()
        if tracker.trtype == "Boolean":
            if new_value.lower() in bools:
                new_value = bools[new_value.lower()]
            else:
                error = "Boolean value is not allowed. Try 'true or false' or '1 or 0'"
                raise InputError(400, "LOG002", error, "trackereditlog.html", tracker=tracker, uname=current_user.uname, condition=True, current=current, lid=lid)
        elif tracker.trtype == "Numerical" or tracker.trtype == "Time Duration":
            new_value = float(new_value)
        if type(new_value) != tracker_types[tracker.trtype]:
            error = "Your value doesn't match the tracker type"
            if tracker.trtype == "Multiple Choice":
                s = Selectables.query.filter_by(trid=trid).first()
                choices = s.choices.split(",")
                raise InputError(400, "LOG001", error, "trackereditlog.html", uname=current_user.uname, tracker=tracker, current=current, condition=False, choices=choices, lid=lid)
            raise InputError(400, "LOG002", error, "trackereditlog.html", tracker=tracker, uname=current_user.uname, condition=True, current=current, lid=lid)
        new_note = request.form.get('note')
        new_timestamp = request.form.get('datetime') 
        log = Logs.query.filter_by(trid=trid).one()
        log.value=new_value
        log.note=new_note
        log.timestamp=new_timestamp
        try:
            db.session.commit()
            return redirect(f"/user/{uname}/{trid}/tracker_info")
        except:
            db.session.rollback()
            raise ServerError(500, "LOG003", "<h1>SERVER ERROR</h1>")


@app.route("/user/<uname>/<int:trid>/<int:lid>/deletelog")
@login_required
def user_log_del(uname, lid, trid):
    log = Logs.query.filter_by(lid=lid).first()
    try:
        db.session.delete(log)
        db.session.commit()
        return redirect(f"/user/{uname}/{trid}/tracker_info")
    except:
        db.session.rollback()
        
        error = "<h1>Something wrong happened. Server Error</h1>"
        raise ServerError(500, "TRACKER003", error_message=error)