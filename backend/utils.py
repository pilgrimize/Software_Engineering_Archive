from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import time

db = SQLAlchemy()

class UserModel(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    pwd = db.Column(db.String(100), nullable=False)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)


class ReportModel(db.Model):
    __tablename__ = "report"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    date = db.Column(db.DateTime, primary_key=True)
    pile_id = db.Column(db.Integer, primary_key=True)
    charge_num = db.Column(db.Integer)
    charge_time = db.Column(db.Integer)
    amount = db.Column(db.Float)
    charge_fee = db.Column(db.Float)
    service_fee = db.Column(db.Float)
    total = db.Column(db.Float)

class Time():
    def __init__(self):
        self.real_begin_time = time.time()
        self.begin_time = 6 * 3600 + 0 * 60 + 0
        self.speed = 60
        self.is_pause = 1
        self.pause_time = self.begin_time
        self.real_pause_time = self.real_begin_time
        self.total_pause_time = 0
        self.plus_time = 0
    def get_time_string(self):
        t = self.get_time_sec()
        return "%d:%02d:%02d" % (t//3600, t % 3600//60, t % 60)

    def get_time_str(self, t):
        # return str(t // 3600) + ":" + str(t % 3600 // 60) + ":" + str(t % 60)
        return "%d:%02d:%02d" % (t//3600, t % 3600//60, t % 60)
    
    def get_time_sec(self):
        if self.is_pause:
            now_time_sec = self.pause_time
        else:
            now_time_sec = int(self.begin_time + self.plus_time + (time.time() - self.real_begin_time - self.total_pause_time) * self.speed)
        return now_time_sec
    def get_time_msec(self):
        if self.is_pause:
            now_time_msec = self.pause_time * 1000
        else:
            now_time_msec = int(self.begin_time + self.plus_time + (time.time() - self.real_begin_time - self.total_pause_time) * self.speed) * 1000 
        return now_time_msec, self.speed
    def time_pause(self):
        if self.is_pause:
            return
        t = time.time()
        self.is_pause = 1
        self.pause_time = int(self.begin_time + self.plus_time + (t - self.real_begin_time - self.total_pause_time) * self.speed)
        self.real_pause_time = t
    def time_start(self):
        if not self.is_pause:
            return
        self.is_pause = 0
        self.total_pause_time += time.time() - self.real_pause_time
    def time_set(self, t):
        if self.is_pause == 0 or self.pause_time > t:
            return False
        self.plus_time += t - self.pause_time
        self.pause_time = t
        return True
    def get_time_stamp(self, time_str):
        hh, mm= map(int, time_str.split(':'))
        return hh*3600 + mm*60


class Authorization:
    def __init__(self, username,pwd,is_admin):
        self.username = username
        self.pwd = pwd
        self.is_admin = is_admin

    def login(self):
        user = UserModel.query.filter_by(username=self.username).first()
        if user is None:
            return False
        if user.username == self.username and user.pwd == self.pwd and user.is_admin == self.is_admin:
            if __debug__:
                print("username:",user.username,"   ","pwd:",user.pwd, "   ","is_admin:",user.is_admin)
            return True
        return False

    def register(self):
        user = UserModel.query.filter_by(username = self.username).first()
        print("user :", user)
        if user is None :
            newUser = UserModel(username=self.username, pwd=self.pwd, is_admin=self.is_admin)
            db.session.add(newUser)
            db.session.commit()
            if __debug__:
                userTest = UserModel.query.filter_by(username=self.username).first()
                print("aseert Succseefully,username:",userTest.username)
            return True
        else:
            return False

class Report():
    def __int__(self,date, pile_id, charge_num, charge_time, amount, charge_fee, service_fee, total):
        self.date = date
        self.pile_id = pile_id
        self.charge_num = charge_num
        self.charge_time = charge_time
        self.amount = amount
        self.charge_fee = charge_fee
        self.service_fee = service_fee
        self.total = total

    def reportStore(self):
        report = ReportModel.query.filter_by(date=self.date, pile_id=self.pile_id).first()
        if report is None:
            newReport = ReportModel(self.date,  self.pile_id ,
                                    self.charge_num, self.charge_time, self.amount,
                                    self.charge_fee, self.service_fee, self.total)
            db.session.add(newReport)
            db.session.commit()
        else:
            report.charge_num = self.charge_num
            report.charge_time = self.charge_time
            report.amount = self.amount
            report.charge_fee = self.charge_fee
            report.service_fee = self.service_fee
            report.total = self.total
            db.session.add(report)
            db.session.commit()

