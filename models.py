from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, current_user

db = SQLAlchemy()

class Users(db.Model, UserMixin):
    __tablename__ = "Users"
    uid = db.Column(db.Integer, autoincrement=True, primary_key=True)
    uname = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String(), nullable=False)
    trackers = db.relationship("Trackers", secondary="Enrollments")

    def get_id(self):
        return (self.uid)


class Trackers(db.Model):
    __tablename__ = "Trackers"
    trid = db.Column(db.Integer, autoincrement=True, primary_key=True)
    trname = db.Column(db.String, nullable=False, unique=True)
    trtype = db.Column(db.String, nullable=False)
    trdesc = db.Column(db.String)

class Selectables(db.Model):
    __tablename__ = "Selectables" 
    sid = db.Column(db.Integer, autoincrement=True, primary_key=True)
    choices = db.Column(db.String, nullable=False)
    trid = db.Column(db.Integer, db.ForeignKey("Trackers.trid"), primary_key=True, nullable=False)


class Logs(db.Model):
    __tablename__ = "Logs"
    lid = db.Column(db.Integer, autoincrement=True, primary_key=True)
    value = db.Column(db.String, nullable=False)
    note = db.Column(db.String)
    timestamp = db.Column(db.String, nullable=False)
    uid = db.Column(db.Integer, db.ForeignKey("Users.uid"), primary_key=True,nullable=False)
    trid = db.Column(db.Integer, db.ForeignKey("Trackers.trid"), primary_key=True, nullable=False)

class Enrollments(db.Model):
    __tablename__ = "Enrollments"
    enrid = db.Column(db.Integer, autoincrement=True, primary_key=True)
    uid = db.Column(db.Integer, db.ForeignKey("Users.uid"), primary_key=True, nullable=False)
    trid = db.Column(db.Integer, db.ForeignKey("Trackers.trid"), primary_key=True, nullable=False)


def init_db():
    db.create_all()

    new_user = Users('a@a.com', 'aaaaaaaa')
    new_user.display_name = 'Sathya'
    db.session.add(new_user)
    db.session.commit()
    new_user.datetime_subscription_valid_until = datetime.datetime(2023, 1, 1)
    db.session.commit()


if __name__ == '__main__':
    init_db()