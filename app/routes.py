from wtforms import form
from app import app, db
from app.forms import LoginForm, RegistrationForm, SurveyForm
from flask import render_template, flash, redirect, url_for, request, abort, jsonify, Response, redirect, send_file
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, SurveyFin, UserResponse
from werkzeug.urls import url_parse
from flask_user import roles_required
from datetime import datetime, timezone
import random
import model_test
import json
import io
import xlwt
import sqlite3
import numpy as np
from excel_methods import  create_value_id_dict,create_statement_id_dict, create_id_value_dict, get_statement_value_list

@app.route('/')
@app.route('/index')
def index():
    model_test.test_function()
    if current_user.is_authenticated:
        return redirect(url_for('admin_view_surveys'))
    
    else:
        return redirect(url_for('login'))

    model_test.test_function()
    return render_template('index.html', title='Home')

@app.route('/test')
def test():
    return render_template('test.html', title='Home')
    
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin_view_surveys'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('admin_view_surveys')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@app.route('/createsurvey', methods=['GET','POST'])
def createSurvey():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    surveys = []
    ## interal class passed to html
    ## holds partial information about a class for visual use only
    surveysDB = SurveyFin.query.filter_by().all()
    for survey in surveysDB:
        if survey.survey_id:
            surveyArray = []
            print("Survey_id = " + survey.survey_id)
            user_id = survey.user_id
            creator_name = User.query.filter_by(id=user_id).first().username
            surveyArray.append(survey.survey_id)
            surveyArray.append(user_id)
            surveyArray.append(creator_name) 
            surveyArray.append(survey.survey_name)
            surveys.append(surveyArray)
    user_id = current_user.id
    form = SurveyForm()
    if request.method=="POST":
        # Survey name
        survey_name = request.form['survey_name']
        # Instructions
        instructions = []
        # First page
        instructions.append([request.form['instructions-start']])
        instructions.append([request.form['instructions-id']])
        instructions.append([request.form['instructions-1']])
        instructions.append([request.form['instructions-2']])
        instructions.append([request.form['instructions-3']])
        instructions.append([request.form['instructions-4']])
        instructions.append([request.form['instructions-5']])
        # Status
        publish = request.form['publish']
        if publish == '1':
            publish = True
        else:
            publish = False

        # Range
        rangeform = request.form.getlist('range')
        survey_range = [int(x) for x in rangeform]
        
        #inbuilt range function doesnt work, DIY
        index = survey_range[0]
        end_range = survey_range[1]
        survey_range = []  
        while(index <= end_range):
            survey_range.append(index)
            index += 1

        # Cols
      
        columns = request.form.getlist('cols')
        columns = columns[0].split(",")

        cols = [int(x) for x in columns]

        # Registration
        final_register = []
        register = request.form.getlist('register')
        max_length = 1
        for question in register:
            options = question.splitlines()
            options_filtered = [string for string in options if string]
            if len(options_filtered) == 2:
                final_register.append([options_filtered[0]])
            else:
                final_register.append(options_filtered)
                if max_length < len(options_filtered):
                    max_length = len(options_filtered)

        # Makes result double array rectangular
        for array in final_register:
            while len(array) < max_length:
                array.append("")

        # Statements
        statements = request.form['statements']
        lines = statements.splitlines()
        lines_filtered = []
        for string in lines:
            if string.replace(" ", "") == "":
                continue
            lines_filtered.append(string)

        # Questionnaire
        questionnaire = request.form.getlist('questionnaire')
        final_questionnaire = []
        # Least
        least = request.form['least-questionnaire']
        if not least.replace(" ", "") == "":
            final_questionnaire.append([least, "least agree"])
        # Most
        most = request.form['most-questionnaire']
        if not most.replace(" ", "") == "":
            final_questionnaire.append([most, "most agree"])

        for question in questionnaire:
            if question.replace(" ", "") == "":
                continue
            final_questionnaire.append([question, ""])


        # Criteria
        criteria = []
        criteria.append(request.form['criteria-negative'])
        criteria.append(request.form['criteria-neutral'])
        criteria.append(request.form['criteria-positive'])

        result = SurveyFin(survey_name=survey_name, instructions=instructions,
                            range=survey_range, cols=cols, register=final_register, statements=lines_filtered, 
                            publish = publish, user_id = user_id,
                            questionnaire=final_questionnaire, criteria=criteria)
        #Push to db
        #try:
        db.session.add(result)
        db.session.commit()
        return redirect('/admin_view_surveys')
        #except:
        #    return "There was an error with adding survey into database"
    else:
        try:
            with open('default.json') as f:
                data = json.load(f)
            instructions = data["instructions"]
            criteria = data["criteria"]
            range = data["range"]
            questionnaire = data['questionnaire']
        except: # If file fails to open, just use these as defaults
            instructions = [[], [], [], [], [], [], []]
            criteria = ["Disagree", "Neutral", "Agree"]
            range = [-3, 3]
            questionnaire = ["Please explain why you rated the statements above as the lowest.","Please explain why you rated the statements above as the highest."]
        return render_template("createsurvey.html", instructions=instructions, criteria=criteria, range=range, questionnaire=questionnaire, surveys = surveys)

#Check survey creation
@app.route('/createsurveyresult', methods=['GET','POST'])
def createSurveyresult():
    form = SurveyForm()
    if request.method=="POST":
        survey_name = request.form['survey_name']
        instructions = request.form.getlist('instructions')
        #publish = request.form['publish']
        rangeform = request.form.getlist('range')
        range = [int(x) for x in rangeform]
        columns = request.form.getlist('cols')
        columns = columns[0].split(",")
        cols = [int(x) for x in columns]
        register = request.form.getlist('register')
        statements = request.form.getlist('statements')
        questionnaire = request.form.getlist('questionnaire')
        criteria = request.form.getlist('criteria')
        result = SurveyFin(survey_name=survey_name, instructions=instructions,  range=range, cols=cols, register=register, statements=statements, questionnaire=questionnaire, criteria=criteria)
        #Push to db
        #try:
        db.session.add(result)
        db.session.commit()
        return redirect('/createsurveyresult')
        #except:
        #    return "There was an error with adding survey into database"
    else:
        survey_name = SurveyFin.query.filter_by(survey_name = SurveyFin.survey_name).first()
        instructions = SurveyFin.query.filter_by(instructions = SurveyFin.instructions).first()
        #publish = SurveyFin.query.filter_by(publish = SurveyFin.publish).first()
        range = SurveyFin.query.filter_by(range = SurveyFin.range).first()
        cols = SurveyFin.query.filter_by(cols = SurveyFin.cols).first()
        register = SurveyFin.query.filter_by(register = SurveyFin.register).first()
        statements = SurveyFin.query.filter_by(statements = SurveyFin.statements).first()
        questionnaire = SurveyFin.query.filter_by(questionnaire = SurveyFin.questionnaire).first()
        criteria = SurveyFin.query.filter_by(criteria = SurveyFin.criteria).first()
        return render_template("createsurveyresult.html", survey_name=survey_name, instructions=instructions, range=range, cols=cols, register=register, statements=statements, questionnaire=questionnaire, criteria=criteria, form=form, result=SurveyFin.query.all())

#This function is ran when button to edit a survey is clicked.
#Takes to editsurvey page for the selected survey
#@app.route("/surveys/editsurvey/<survey_id>", methods=['GET','POST'])
#def editsurvey(survey_id):
    #select row from SurveyFin table for name passed from list page
    #edit = SurveyFin.query.filter_by(survey_id = survey_id).all()
    #edit=db.engine.execute("SELECT * FROM \"Survey Fin\" where survey_id=survey_id",{"survey_id":survey_id})
    #display data in modify page passing the tuple as parameter in render_template method
    #return render_template("editsurvey.html",edit=edit)

@app.route("/surveys/editsurvey/<survey_id>", methods=['GET','POST'])
def editsurvey(survey_id):
    #select row from SurveyFin table for name passed from list page
    survey = SurveyFin.query.filter_by(survey_id = survey_id).first()
    frames = ""
    for x in survey.cols:
        frames += "1fr " 
    count = sum(survey.cols)
    
    #edit=db.engine.execute("SELECT * FROM \"Survey Fin\" where survey_id=survey_id",{"survey_id":survey_id})
    #display data in modify page passing the tuple as parameter in render_template method
    return render_template("editsurvey.html",sum=count,frames=frames, survey=survey)

@app.route("/surveyUpdate/<survey_id>", methods=["POST"])
def surveyUpdate(survey_id):
    print("UPDATe")
    print(survey_id)
    #store values recieved from HTML form in local variables
    user_id = current_user.id
    form = SurveyForm()
    update = SurveyFin.query.filter_by(survey_id = survey_id).first()
    survey_id = survey_id
    update.survey_name = request.form['survey_name']

    instructions = []
        # First page
    instructions.append([request.form['instructions-start']])
    instructions.append([request.form['instructions-id']])
    instructions.append([request.form['instructions-1']])
    instructions.append([request.form['instructions-2']])
    instructions.append([request.form['instructions-3']])
    instructions.append([request.form['instructions-4']])
    instructions.append([request.form['instructions-5']])

    update.instructions = instructions
    
    # Status
    publish = request.form['publish']
    if publish == '1':
        publish = True
    else:
        publish = False

    update.publish = publish

    rangeform = request.form.getlist('range')
    survey_range = [int(x) for x in rangeform]
    #inbuilt range function doesnt work, DIY
    index = survey_range[0]
    end_range = survey_range[1]
    survey_range = []  
    while(index <= end_range):
        survey_range.append(index)
        index += 1
    update.range = survey_range

    # Cols
    columns = request.form.getlist('cols')
    print(request.form)
    columns = columns[0].split(",")
    cols = [int(x) for x in columns]
    update.cols = cols

    # Registration
    final_register = []
    register = request.form.getlist('register')
    max_length = 1
    for question in register:
        options = question.splitlines()
        options_filtered = [string for string in options if string]
        if len(options_filtered) == 2:
            final_register.append([options_filtered[0]])
        else:
            final_register.append(options_filtered)
            if max_length < len(options_filtered):
                max_length = len(options_filtered)
    
    # Makes result double array rectangular
    for array in final_register:
        while len(array) < max_length:
            array.append("")
    
    update.register = final_register



    # Statements
    statements = request.form['statements']
    lines = statements.splitlines()
    lines_filtered = []
    for string in lines:
        if string.replace(" ", "") == "":
            continue
        lines_filtered.append(string)

    update.statements = lines_filtered

    # Questionnaire
    questionnaire = request.form.getlist('questionnaire')
    final_questionnaire = []
    # Least
    least = request.form['least-questionnaire']
    if not least.replace(" ", "") == "":
        final_questionnaire.append([least, "least agree"])
    # Most
    most = request.form['most-questionnaire']
    if not most.replace(" ", "") == "":
        final_questionnaire.append([most, "most agree"])

    for question in questionnaire:
        if question.replace(" ", "") == "":
            continue
        final_questionnaire.append([question, ""])

    update.questionnaire = final_questionnaire


    # Criteria
    criteria = []
    criteria.append(request.form['criteria-negative'])
    criteria.append(request.form['criteria-neutral'])
    criteria.append(request.form['criteria-positive'])
    
    #Execute update query
    db.session.commit()
    #NEED TO UPDATE RENDER_TEMPLATE TO SURVEY VIEW PAGE
    return redirect(url_for('admin_view_surveys'))


#Gets values from the survey edit page, and updates the database
#Need to update route and render_template
#@app.route("/surveyUpdate/<survey_id>", methods=["POST"])
#def surveyUpdate(survey_id):
    #store values recieved from HTML form in local variables
    form = SurveyForm()
    user_id = current_user.id
    survey_id = SurveyFin.survey_id
    survey_name = request.form['survey_name']
    instructions = request.form.getlist('instructions')
    publish = bool(request.form['publish'])
    rangeform = request.form.getlist('range')
    survey_range = [int(x) for x in rangeform]
    
    #inbuilt range function doesnt work, DIY
    index = survey_range[0]
    end_range = survey_range[1]
    survey_range = []  
    while(index <= end_range):
        survey_range.append(index)
        index += 1

    columns = request.form.getlist('cols')

    columns = columns[0].split(",")
    cols = [int(x) for x in columns]
    #TODO add multi-choice support for below
    register = request.form.getlist('register')
    final_register = []
    for question in register:
        arr = []
        arr.append(question)
        final_register.append(arr)
    statements = request.form.getlist('statements')
    questionnaire = request.form.getlist('questionnaire')
    final_questionnaire = []
    for question in questionnaire:
        arr = []
        arr.append(question)
        final_questionnaire.append(arr)
    print (questionnaire)
    criteria = request.form.getlist('criteria')
    #create string update query with the values from form
    strSQl= "update \"Survey Fin\" set survey_name='"+survey_name+"', instructions='"+instructions+"',publish='"+publish+"', range=" +survey_range+"' ,cols='"+cols+"', register='"+final_register+"', statements='"+statements+"', publish='"+publish+"', user_id='"+user_id+"', questionnaire='"+final_questionnaire+"', criteria='"+criteria+" where survey_id="+str(survey_id)
    #Execute update query
    db.engine.execute(strSQl) 
    #commit to database
    db.commit() 
    #NEED TO UPDATE RENDER_TEMPLATE TO SURVEY VIEW PAGE
    return render_template("admin_view_surveys.html")


#Need to update routes and render_template
@app.route("/surveyDuplicate/<survey_id>", methods=['GET','POST'])
def Duplicate_Survey(survey_id):
    survey_to_duplicate = SurveyFin.query.filter_by(survey_id = survey_id)[0]
  
    result = SurveyFin(survey_name=survey_to_duplicate.survey_name, instructions=survey_to_duplicate.instructions,
                            range=survey_to_duplicate.range, cols=survey_to_duplicate.cols, register=survey_to_duplicate.register, statements=survey_to_duplicate.statements, 
                            publish = survey_to_duplicate.publish, user_id = survey_to_duplicate.user_id,
                            questionnaire=survey_to_duplicate.questionnaire, criteria=survey_to_duplicate.criteria)
    
    
    db.session.add(result)
    db.session.commit()
    # survey_to_delete = SurveyFin.query.filter_by(survey_id = survey_id).delete()
    # db.session.commit() 
    if "master_admin_view_surveys" in request.referrer:
        return redirect(url_for('master_admin_view_surveys'))
    else:
         return redirect(url_for('admin_view_surveys'))

    
#Need to update routes and render_template
@app.route("/surveyDelete/<survey_id>", methods=['GET','POST'])
def Delete_Survey(survey_id):
    survey_to_delete = SurveyFin.query.filter_by(survey_id = survey_id).delete()
    db.session.commit() 
    if "master_admin_view_surveys" in request.referrer:
        return redirect(url_for('master_admin_view_surveys'))
    else:
         return redirect(url_for('admin_view_surveys'))

@app.route("/responseDelete/<survey_id>/<response_id>", methods=['GET','POST'])
def Delete_Response(survey_id, response_id):
    response_to_delete = UserResponse.query.filter_by(id = response_id, surveyid = survey_id).delete()
    db.session.commit() 
    return redirect(url_for('admin_downloads',survey_id = survey_id))


@app.route('/logout')
def logout():
    logout_user()
    flash('Logged out successfully')
    return redirect(url_for('login'))

# the next code should cover this section
# @app.route('/register', methods=['GET', 'POST'])
# def register():
 #   if current_user.is_authenticated:
  #      return redirect(url_for('index'))
   # if form.validate_on_submit():
    #   user = User(username=form.username.data, email=form.email.data)
    #  user.set_password(form.password.data)
    # db.session.add(user)
     # db.session.commit()
     #flash('Congratulations, you are now a registered user!')
     # return redirect(url_for('login'))
    # return render_template('register.html', title='Register', form=form)

# Only admin creates users, the route is made up, feel free to edit!


@app.route('/admin/create_user', methods=['GET', 'POST'])
@roles_required('MASTER_ADMIN')
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    else:
        form = RegistrationForm(request.form)
        if(request.method == 'POST' and form.validate_on_submit()):
            email = form.email.data
            password = form.password.data
            if User.query.filter_by(User.email == email).first():
                flash('Email is associated with another user')
                return redirect(url_for('index'))
            else:
                user = User()
                user.username = form.username.data
                user.email = form.email.data
                user.set_password(form.password.data)
                db.session.add(user)
                db.session.commit()
                flash('Congratulations, you are now a registered user!')
                return redirect(url_for('login'))
        return render_template('register.html', title='Register', form=form)

@app.route('/survey/<survey_id>')
#@login_required
def survey(survey_id):

    q = SurveyFin.query.filter_by(survey_id = survey_id).first_or_404()
    
    survey_name = q.survey_name
    registration_raw = q.register
    registration = []
    for arr in registration_raw:
        registration.append([val for val in arr if val != ""])
    questionnaire = q.questionnaire
    statements = q.statements
    criteria = q.criteria
    instructions_raw = q.instructions
    instructions = []
   
    for arr in instructions_raw:
        instructions.append([val for val in arr if val != ""])
    
    print(instructions)
    condition = instructions[3]
    print(condition)
    cols = q.cols
    rows = q.range
    frames = ""
    for x in q.cols:
        frames += "1fr " 

    width = ""
   
    if len(q.range) <= 7:
        width = "100"
    elif 8<= len(q.range) <= 11:
        width="70"
    else: 
        width= "50"
    

    return render_template('survey.html', width=width, frames=frames, title=survey_name, registration=registration, 
        questionnaire=questionnaire, statement_list=statements, criteria=criteria, cols=cols, 
        rows=rows, survey_id=survey_id, instructions=instructions, condition=condition)

# This route is called when a section of the survey is received
@app.route('/receive', methods=['POST', 'GET'])
def receive():
    if request.method == 'POST':
        data = request.get_json()
        # What section of the survey was just received?
        section = data["progress"]
        survey_id = data["surveyId"]
        user_id = data["userId"]

        if section == 1:
            register = data["register"]
            
            commit = UserResponse(survey_id=survey_id, id=int(user_id), progress=section, register=register)
            db.session.add(commit)
            db.session.commit()

            ########### When the survey is started, record time started
            user_response_id = UserResponse.query.filter_by(id=user_id).first()
            user_response_id.timestart = datetime.now(timezone.utc)
            db.session.commit()

        elif section == 2:
            negative = data["negative"]
            neutral = data["neutral"]
            positive = data["positive"]

            commit = UserResponse.query.filter_by(id=int(user_id)).first()
            commit.sort_disagree = negative
            commit.sort_neutral = neutral
            commit.sort_agree = positive
            commit.progress = section
            db.session.commit()

            ########### When section is submitted, calculate timestart, end and time spent
            user_response_id = UserResponse.query.filter_by(id=user_id).first()
            user_response_id.timeend = datetime.now(timezone.utc)
            db.session.commit()
            ########## Subtract timestart and timeend columns
            user_response_id = UserResponse.query.filter_by(id=user_id).first()
            user_response_id.timespent = user_response_id.timeend - user_response_id.timestart
            db.session.commit()
            user_response_id.timestart = datetime.now(timezone.utc)
            db.session.commit()

        elif section == 3:
            matrix = data["matrix"]

            commit = UserResponse.query.filter_by(id=int(user_id)).first()
            commit.matrix = matrix
            commit.progress = section
            db.session.commit()

            ########### When section is submitted, calculate timestart, end and time spent
            user_response_id = UserResponse.query.filter_by(id=user_id).first()
            user_response_id.timeend = datetime.now(timezone.utc)
            db.session.commit()
            ########## Subtract timestart and timeend columns
            user_response_id = UserResponse.query.filter_by(id=user_id).first()
            user_response_id.timespent = user_response_id.timespent + (user_response_id.timeend - user_response_id.timestart)
            db.session.commit()
            user_response_id.timestart = datetime.now(timezone.utc)
            db.session.commit()
        elif section == 4:
            question = data["question"]

            commit = UserResponse.query.filter_by(id=int(user_id)).first()
            commit.question_ans = question
            commit.progress = section
            db.session.commit()

            ########### When section is submitted, calculate timeend and time spent
            user_response_id = UserResponse.query.filter_by(id=user_id).first()
            user_response_id.timeend = datetime.now(timezone.utc)
            db.session.commit()
            ########## Subtract timestart and timeend columns
            user_response_id = UserResponse.query.filter_by(id=user_id).first()
            user_response_id.timespent = user_response_id.timespent + (user_response_id.timeend - user_response_id.timestart)
            user_response_id.timespent = str(user_response_id.timespent).split(".")[0]
            db.session.commit()

        return "", 200
    elif request.method == 'GET':
        abort(404)

@app.route('/startSurvey', methods=['POST', 'GET'])
def startSurvey():
    if request.method == 'POST':
        data = request.get_json()
        responseType = data["responseType"]
        
        # They are resuming a survey
        if responseType == 1:
            user_id = data["user_id"]
            # just here for now because integer

            commit = UserResponse.query.filter_by(id=user_id).first()

            ########### When the survey is started, record time started
            user_response_id = UserResponse.query.filter_by(id=user_id).first()
            user_response_id.timestart = datetime.now(timezone.utc)
            db.session.commit()

            if(user_id != ""):
                user_id = int(user_id)
            else:
                user_id = 0

            q = UserResponse.query.filter_by(id = user_id).first()

            if q is None:
                return "Reponse ID not found", 400
            else:
                progress = q.progress
                negative_sort = []
                neutral_sort = []
                positive_sort = []
                matrix = []
                if progress > 1:
                    negative_sort = q.sort_disagree
                    neutral_sort = q.sort_neutral
                    positive_sort = q.sort_agree
                    matrix = q.matrix
                obj = {
                    'progress' : progress,
                    'user_id' : str(user_id),
                    'negative_sort' : negative_sort,
                    'neutral_sort' : neutral_sort,
                    'positive_sort' : positive_sort,
                    'matrix' : matrix
                }
                return obj, 200
        else:
            q = None
            # They are starting a new survey
            user_id = random.randint(1, 1000000) # Temporarily an integer
            # This query SHOULD be None, i.e. it is a brand new user id
            q = UserResponse.query.filter_by(id = str(user_id)).first()

            while q is not None:
                user_id = random.randint(1, 1000) # Temporarily an integer
                q = UserResponse.query.filter_by(id = str(user_id)).first()

                ########### When the survey is started, record time started
                user_response_id = UserResponse.query.filter_by(id=int(id)).first()
                user_response_id.timestart = datetime.now(timezone.utc)
                db.session.commit()

            return str(user_id), 200

    elif request.method == 'GET':
        abort(404)

# Admin-related routes below

@app.route('/admin_view_surveys')
@login_required
def admin_view_surveys():
    # Paramter to be passed render templates function
    surveys = []
    ## interal class passed to html
    ## holds partial information about a class for visual use only
    class psuedo_survey:
        def __init__(self,survey_id,survey_creator,survey_name,num_responses, published):
            self.survey_id = survey_id
            self.survey_creator = survey_creator 
            self.survey_name = survey_name 
            self.num_responses = num_responses
            self.published = published


    creator_name = current_user.username
    #get all surveys made by that person
    surveysDB = SurveyFin.query.filter_by(user_id = current_user.id).all()

    for survey in surveysDB:
        num_responses = UserResponse.query.filter_by(surveyid = str(survey.survey_id)).count()
        print("Survey_id = " + survey.survey_id)
        surveys.append(psuedo_survey(survey.survey_id, creator_name, survey.survey_name, num_responses,survey.publish))

    return render_template('admin_view_surveys.html', surveys = surveys)

@app.route('/master_admin_view_surveys')
@login_required
def master_admin_view_surveys():
    if current_user.username !="TU":
        return redirect(url_for('admin_view_surveys'))
        # Paramter to be passed render templates function
    surveys = []
    ## interal class passed to html
    ## holds partial information about a class for visual use only
    class psuedo_survey:
        def __init__(self,survey_id,survey_creator,survey_name,num_responses, published):
            self.survey_id = survey_id
            self.survey_creator = survey_creator 
            self.survey_name = survey_name 
            self.num_responses = num_responses
            self.published = published
    #
    surveysDB = SurveyFin.query.filter_by().all()
    for survey in surveysDB:
        num_responses = UserResponse.query.filter_by(surveyid = str(survey.survey_id)).count()
        if survey.survey_id:
            print("Survey_id = " + survey.survey_id)
            user_id = survey.user_id
            creator_name = User.query.filter_by(id=user_id).first().username
            surveys.append(psuedo_survey(survey.survey_id, creator_name, survey.survey_name, num_responses,survey.publish))
    return render_template('admin_view_surveys.html', surveys = surveys)

@app.route('/admin_downloads/<survey_id>')
def admin_downloads(survey_id):
    responses = UserResponse.query.filter_by(surveyid = survey_id).all()
    response = responses.sort(key=lambda x: x.timeend, reverse=True)
    # Get survey id of response
    surveysDB = SurveyFin.query.filter_by(survey_id = survey_id).all()
    q_sort_statements = surveysDB[0].statements
    statement_id_dict = create_statement_id_dict(q_sort_statements)
    return render_template('admin_downloads.html', responses=responses, surveysDB=surveysDB, statement_id_dict = statement_id_dict)

@app.route('/admin_user')
def admin_user():
    return render_template('admin_user.html', current_user = current_user)

@app.route('/download')
#this is a test route. 
#FOR TEST USE ONLY
def download():
    #output in bytes
    output = io.BytesIO()
    #create WorkBook object
    workbook = xlwt.Workbook()
    #add a sheet
    sh = workbook.add_sheet('Employee Report')
   
    #add headers
    sh.write(0, 0, 'Emp Id')
    sh.write(0, 1, 'Emp First Name')
    sh.write(0, 2, 'Emp Last Name')
    sh.write(0, 3, 'Designation')
   
    workbook.save(output)
    output.seek(0)
   
    return Response(output, mimetype="application/ms-excel", headers={"Content-Disposition":"attachment;filename=employee_report.xls"})


#Route for survey bulk download
@app.route('/admin_downloads/<survey_id>/bulk_download',methods=['GET','POST'])
@login_required
def admin_bulk_download_survey_responses(survey_id):
    rows = request.args.get('rows')
    print(type(rows) )
    finished = 4 # the number of the progress if the response is finished
    survey = SurveyFin.query.filter_by(survey_id = survey_id).first()
    responses = UserResponse.query.filter_by(surveyid = survey_id, progress = finished).all()

    if(responses==[]):
        flash('Cannot Bulk download a survey with no responses')
        return redirect(url_for('admin_downloads',survey_id = survey_id))

    survey_name = survey.survey_name

    #extract matrix data
    q_sort_statements = survey.statements

    #create a dictionary that maps statements to IDs
    #ids = index of statement in the db array
    statement_id_dict = create_statement_id_dict(q_sort_statements)
   
    #Begin excel work
    #output in bytes
    output = io.BytesIO()
    #create WorkBook object
    workbook = xlwt.Workbook()
    #add a sheet
    sh = workbook.add_sheet('Bulk Download')
   
    #add headers
    #starting at 4,1 because i like whitespace at top of excel file
    start_row = 4
    start_col = 1
    if rows == "1":
        sh.write(start_row,start_col,"Statement IDs")
        sh.write(start_row,start_col + 1,"Response IDs")
    elif rows =="2":
        sh.write(start_row,start_col,"Value")
        sh.write(start_row,start_col + 1,"Response IDs")
    elif rows== "3":
        sh.write(start_row,start_col,"Register Questions")
        sh.write(start_row,start_col + 1,"Response IDs")
    else:
        sh.write(start_row,start_col,"Post Survey Questions")
        sh.write(start_row,start_col + 1,"Response IDs")
    
   

    #set row,column to begin writing data
    #sh.write(Row, column, "data")
    start_row = start_row + 1
    num_responses = len(responses)

    #write the response ids
    for index in range(0,num_responses):
        sh.write(start_row, start_col + 1 + index,"{}".format(responses[index].id))
    start_row += 1

    survey_range = survey.range
    survey_cols =  responses[0].matrix
    survey_rows = list(np.transpose(np.array(survey_cols)))

    #Write all possible values down the left side
    if rows == "1":
        row_iterator = start_row
        sorted_statement_ids = sorted(statement_id_dict.values())
        statement_value_list = get_statement_value_list(survey_range,responses,statement_id_dict)
        

        for i in range(0, len(sorted_statement_ids )):
            sh.write(row_iterator, start_col, sorted_statement_ids[i])
            row_iterator += 1
        start_col +=1
        
        for response in statement_value_list:
            row_iterator = start_row
            for statement_id in sorted_statement_ids:
                value = response.get(statement_id)
                sh.write(row_iterator, start_col, value)
                row_iterator += 1
            start_col +=1
        
    elif rows=="2":
        statement_value_list = get_statement_value_list(survey_range,responses,statement_id_dict)
        
        #write down all possible values
        row_iterator = start_row
        for item in statement_value_list[0].items():
            sh.write(row_iterator, start_col, item[1])
            row_iterator += 1


        #set excel coords to correct position
        start_col +=1


        ###### Populate user data

        #Every element in this list is a list describing a particular user response
        # each list contains a list of tuples such that (statement id, value)
        # each list is sort by ascending value
      
        for response in statement_value_list:
            #set curser to top of sheet
            row_iterator = start_row
            for item in response.items():
                #write down all statement_ids
                sh.write(row_iterator, start_col, item[0])
                row_iterator += 1
            #move to next col for next response
            start_col +=1
   
    elif rows=="3":
        row_iterator = start_row
        for question in survey.register:
            sh.write(row_iterator, start_col, question)
            row_iterator += 1

        #set excel coords to correct position
        start_col +=1

        for response in responses:
            row_iterator = start_row
            for i in range(0, len(survey.register)):
                sh.write(row_iterator, start_col, response.register_ans[i])
                row_iterator += 1
            #move to next col for next response
            start_col +=1
    else:
         row_iterator = start_row
         for question in survey.questionnaire:
             sh.write(row_iterator, start_col, question[0])
             row_iterator += 1

         #set excel coords to correct position
         start_col +=1
         for response in responses:
            row_iterator = start_row
            for i in range(0, len(survey.questionnaire)):
                sh.write(row_iterator, start_col, response.question_ans[i])
                row_iterator += 1
            #move to next col for next response
            start_col +=1


        #  response.question_ans
    
    workbook.save(output)
    output.seek(0)
    return Response(output, mimetype="application/ms-excel", headers={"Content-Disposition":"attachment;filename={}_Bulk_download.xls".format("QMethodSurvey")})
        



#Route for individual excel sheet downloadn
@app.route('/admin_downloads/<survey_id>/<response_id>')
@login_required
def admin_download_survey_response(survey_id,response_id):
    #Get survey data from db
    survey = SurveyFin.query.filter_by(survey_id = survey_id).first()
    response = UserResponse.query.filter_by(id = response_id, surveyid = survey_id).first()

    #extract matrix data
    q_sort_statements = survey.statements
    
    #create a dictionary that maps statements to IDs
    #ids = index of statement in the db array
    statement_id_dict = create_statement_id_dict(q_sort_statements)
    print(statement_id_dict)

    #TODO fix / neaten later, this does not work for non-symetrical surveys
    survey_range = survey.range # list of all possible values
    cols = np.array(response.matrix)
    rows = list(np.transpose(cols))
   
    num_rows = len(rows)

    #create empty dict to match statement ids to values
    id_value_dict = {}


    #iterate over each statement in grid
    #add their value to id_value dict
    for row_index in range(0, num_rows):# go through each row
        row = rows[row_index]
        element_index = 0
    #in each row, check each element
        for element_index in range(0,len(row)):
            element  = row[element_index]
            if element == "":
            #skip empty elements
                continue
            else:
                statement_id =  statement_id_dict[element]
                element_value = survey_range[element_index]
                id_value_dict[statement_id] = element_value

    
    #convert id_value dict to array of tuples: (key,value)
    # ascending order
    sorted_id_by_values = sorted(id_value_dict.items(), key = lambda x:x[1])
    num_items = len(sorted_id_by_values)

    #Begin excel work
    #output in bytes
    output = io.BytesIO()
    #create WorkBook object
    workbook = xlwt.Workbook()
    #add a sheet
    sh = workbook.add_sheet('User Response {user_resp}'.format(user_resp = response.id))
   
    #add headers
    #starting at 4,1 because i like whitespace at top of excel file
    start_row = 4
    start_col = 1
    sh.write(start_row,start_col,"Value")
    sh.write(start_row,start_col + 1,"Statement ID")

    #set row,column to begin writing data
    #sh.write(Row, column, "data")
    start_row = start_row + 1
    for element in sorted_id_by_values:
        value = element[1]
        print("Value : " + str(value))
        statement_id = element[0]
        print("statement_id : " + str(statement_id))
        #write value
        sh.write(start_row,start_col, value)
        sh.write(start_row,start_col + 1, statement_id)
        start_row = start_row + 1
    
    workbook.save(output)
    output.seek(0)
   
    return Response(output, mimetype="application/ms-excel", headers={"Content-Disposition":"attachment;filename=User_Response {user_resp}.xls".format(user_resp = response.id)})



@app.route('/admin_downloads/admin_view_response/<survey_id>/<response_id>')
@login_required
def admin_view_response(survey_id, response_id):
    survey = SurveyFin.query.filter_by(survey_id = survey_id).first()
    response = UserResponse.query.filter_by(surveyid = survey_id, id = response_id).first()
    #from the matrix from rows
    cols = np.array(response.matrix)
    matrix = list(np.transpose(cols))
    survey_range = survey.range
    return render_template('admin_view_response.html', survey = survey, response = response, matrix = matrix, survey_range = survey_range)

@app.route('/redirect/survey', methods=['GET', 'POST'])
def redirect_survey():
    if request.method == "GET":
        abort(404)
    elif request.method == "POST":
        return redirect(url_for('survey', survey_id=request.form["survey-id"]))