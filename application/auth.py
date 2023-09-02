#Imports
from flask_pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from flask import render_template, Blueprint, redirect, url_for, flash, session
from .forms import LoginForm, CreatePlayerAccountForm, CreateManagerAccountForm

auth = Blueprint('auth', __name__)

client = MongoClient('localhost', 27017)
db = client.footballRecommender
user_collection = db.users
teams_collection = db.teams

@auth.route('/login', methods = ['GET', 'POST'])
def login():
    #Logs in user.
    
    form = LoginForm()
    if form.validate_on_submit():
        if user_collection.count_documents({ 'email' : form.email.data }) == 1:
            user = user_collection.find_one({ 'email' : form.email.data })
            if check_password_hash(user['password'], form.password.data):
                session['email'] = user['email']
                session['accountType'] = user['accountType']
                flash('You have been logged in succesfully!')
                return redirect(url_for('main.homepage'))
            else:
                flash('Password is incorrect!')
                return redirect(url_for('auth.login'))
        else:
            flash('Email does not exist! Please check spelling')
            return redirect(url_for('auth.login'))
    return render_template('login.html', form = form)

@auth.route('/createAccount', methods = ['GET'])
def createAccount():
    #Renders template 'createAccount.html'

    return render_template('createAccount.html')

@auth.route('/createAccount/<type>', methods = ['GET', 'POST'])
def createTypeSpecificAccount(type):
    #Creates certain type of account depending on the value of 'type'
    #Type element of {'Player', 'Manager'}

    if type == 'Player':
        form = CreatePlayerAccountForm()
        if form.validate_on_submit():
            if user_collection.count_documents({ 'email' : form.email.data }) == 1:
                flash('An account with this email already  exists')
                return redirect(url_for('auth.createTypeSpecificAccount', type = 'Player'))
            userPlayer = { 'name' : form.name.data, 'email' : form.email.data, 'accountType' : 'Player', 'profileCreated' : False, 'birthday' : ((form.birthday_GMT.data).strftime('%Y/%m/%d')), 'password' : generate_password_hash(form.password.data)}
            user_collection.insert_one(userPlayer)
            session['email'] = form.email.data
            session['accountType'] = 'Player'
            flash('Account created! Now create your player profile!')
            return redirect(url_for('main.manageProfile'))
        return render_template('createPlayerAccount.html', form = form)
    elif type == 'Manager':
        form = CreateManagerAccountForm()
        if form.validate_on_submit():
            if user_collection.count_documents({ 'email' : form.email.data }) == 1:
                flash('An account with this email already  exists')
                return redirect(url_for('auth.createTypeSpecificAccount', type = 'Manager'))
            if teams_collection.count_documents({ 'team_name' : (form.team.data).upper() }) == 1:
                flash('This team already exists! Please ask the manager to delete the team.')
                return redirect(url_for('auth.createTypeSpecificAccount', type = 'Manager'))
            
            userManager = { 'name' : form.name.data, 'email' : form.email.data, 'accountType' : 'Manager', 'profileCreated' : False, 'birthday' : ((form.birthday_GMT.data).strftime('%Y/%m/%d')), 'teamManaged' : (form.team.data).upper(), 'password' : generate_password_hash(form.password.data)}
            user_collection.insert_one(userManager)
            session['email'] = form.email.data
            session['accountType'] = 'Manager'
            flash('Account created! Now create your team profile!')
            return redirect(url_for('main.manageProfile'))
        return render_template('createManagerAccount.html', form = form)

@auth.route('/logout')
def logout():
    #Logs out user

    if session.get('email') == None:
        flash('You were not logged in initially! No action has been performed.')
        return redirect(url_for('main.homepage'))

    session.pop('email', None)
    session.pop('accountType', None)
    flash('You have been logged out succesfully!')
    return redirect(url_for('main.homepage'))