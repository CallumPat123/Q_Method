from flask_security import RoleMixin, UserMixin
from flask_sqlalchemy import SQLAlchemy
from app import app, db, login_manager
from app import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from sqlalchemy.dialects import postgresql
from sqlalchemy.dialects.postgresql import JSON, ARRAY
from sqlalchemy.ext.mutable import Mutable
from sqlalchemy.sql.sqltypes import Boolean, DateTime, Integer, String, Text
from flask_login import UserMixin, AnonymousUserMixin, current_user  # login_manager
from flask import Flask, current_app, redirect, url_for
import uuid  # for ID generation
# flask admin
from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView


@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

# roles may have to be preset before hand-off


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50), unique=True)

    def __init__(self, name: String):
        self.name = name

    def __repr__(self):
        return '<Role %r>' % (self.name)

# User model


class User(db.Model, UserMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer(), primary_key=True)
    email = db.Column(db.String(255), nullable=False, unique=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password_hash = db.Column(db.String(128), nullable=False)
    first_name = db.Column('first name', db.String(50), nullable=False)
    last_name = db.Column('last name', db.String(50), nullable=False)

    # relationship
    roles = db.relationship('Role', secondary='user_roles')
    # second relationship trial, user is parent and has many surveys
    surveys_created = db.relationship('SurveyFin', backref='user')
    #surveyscreated = db.Column(ARRAY(db.Integer), db.ForeignKey(SurveyFin.id))

    def __init__(self, email: String, username: String, password_hash: String,
                 first_name: String, last_name: String, role: Role):
        self.email = email
        self.username = username
        self.password_hash = password_hash
        self.first_name = first_name
        self.last_name = last_name
        self.role = role

    # might not be necessary

    def check_password(self, password):
        return self.password_hash == password


# User-Role association table
class UserRole(db.Model):
    __tablename__ = "user_roles"
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey(
        'users.id', ondelete='CASCADE'), nullable=False)
    role_id = db.Column(db.Integer(), db.ForeignKey(
        'roles.id', ondelete='CASCADE'), nullable=False)


@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


# Survey model,
# Represents a survey that an admin has created, i.e no user responses
class SurveyFin(db.Model):
    __tablename__ = 'Survey Fin'
    id = db.Column(db.Integer, primary_key=True)
    survey_id = db.Column(db.String(128), unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    publish = db.Column(db.Boolean)
    survey_name = db.Column(db.String(200), index=True, nullable=False)
    range = db.Column(ARRAY(db.Integer))
    # columns
    cols = db.Column(ARRAY(db.Integer))
    # instructions for each survey
    instructions = db.Column(ARRAY(db.Text()))
    # register
    register = db.Column(ARRAY(db.Text()))
    # list of statements for a survey
    statements = db.Column(ARRAY(db.Text()))
    # list of questions in a survey
    questionnaire = db.Column(ARRAY(db.Text()))
    criteria = db.Column(ARRAY(db.Text()))

    def __init__(self, user_id: int, publish: bool, survey_name: str,
                 range: list = None, cols: list = None, instructions: list = None,
                 register: list = None, statements: list = None, questionnaire: list = None, criteria: list = None):
        self.survey_id = uuid.uuid4()
        self.user_id = user_id
        self.publish = publish
        self.survey_name = survey_name
        self.range = range
        self.cols = cols
        # register
        self.register = register
        # list of statements for a survey
        self.statements = statements
        # list of questions in a survey
        self.questionnaire = questionnaire
        self.criteria = criteria
        self.instructions = instructions

    def __repr__(self):
        return '<SurveyFin: {}>'.format(self.id)


class UserResponse(db.Model):
    __tablename__ = 'User Response'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, unique=True)
    surveyid = db.Column(db.String(128), db.ForeignKey(
        SurveyFin.survey_id, ondelete='CASCADE'))
    # Registered answers
    register_ans = db.Column(ARRAY(db.Text()))
    # Survey progress
    progress = db.Column(db.Integer)
    # Answer to the question
    question_ans = db.Column(ARRAY(db.Text()))
    # Sort
    sort_agree = db.Column(ARRAY(db.Text()))
    sort_neutral = db.Column(ARRAY(db.Text()))
    sort_disagree = db.Column(ARRAY(db.Text()))
    # Q-sort
    matrix = db.Column(ARRAY(db.Text()))
    timestart = db.Column(db.DateTime, default=datetime.utcnow)
    timeend = db.Column(db.DateTime, default=datetime.utcnow)
    timespent = db.Column(db.Interval)

    def __init__(self, id: int, survey_id: str, progress: int, user_id=None, register=None, question=None, agree=None,
                 neutral=None, disagree=None, matrix=None, timestart=None, timeend=None, timespent=None):
        self.id = id
        self.surveyid = survey_id
        self.user_id = user_id
        self.register_ans = register
        self.progress = progress
        self.question_ans = question
        self.sort_agree = agree
        self.sort_neutral = neutral
        self.sort_disagree = disagree
        self.matrix = matrix
        self.timestart = timestart
        self.timeend = timeend
        self.timespent = timespent

    def __repr__(self):
        return '<UserResponse: {}>'.format(self.id)

# class Admin(db.Model):
#    __tablename__ = 'Admin'
#    id = db.Column(db.Integer, primary_key=True)
#    username = db.Column(db.String(200))
 #   password = db.Column(db.String(128))
 #   Is_SuperAdmin = db.Column(db.Boolean)
 #   surveyscreated = db.Column(ARRAY(db.Integer), db.ForeignKey(SurveyFin.id))

 #   def __repr__(self):
 #       return '<Admin: {}>'.format(self.id)

# class Grid(db.Model):

# export const GridTemplates = [
#    { label: '+3 to -3', val: '7', default_cols: [2, 3, 4, 5, 4, 3, 2], max_statements: 23 },
#    { label: '+4 to -4', val: '9', default_cols: [2, 3, 4, 5, 6, 5, 4, 3, 2], max_statements: 34 },
#    { label: '+5 to -5', val: '11', default_cols: [2, 3, 4, 5, 6, 7, 6, 5, 4, 3, 2], max_statements: 47}
# ];


# anonymous/users
class AnonymousUser(AnonymousUserMixin):
    # default code
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False


login_manager.anonymous_user = AnonymousUser

# master admin
admin = Admin(app, name='qmethodology', template_mode='bootstrap4')


class MyModelView(ModelView):
    # the below function restricts access to the admin interface
    def is_accessible(self):
        return current_user.username == "TU"

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for("admin_view_surveys"))


admin.add_view(MyModelView(User, db.session))
admin.add_view(MyModelView(Role, db.session))
admin.add_view(MyModelView(SurveyFin, db.session))
admin.add_view(MyModelView(UserResponse, db.session))

db.create_all()
