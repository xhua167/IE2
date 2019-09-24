from flask import render_template, url_for, flash, redirect, request
from flaskweb import app, db, bcrypt
from flaskweb.forms import RegistrationForm, LoginForm, RatingForm, SearchForm
from flaskweb.getData import getServices, getInfo, pass_today, updateRating, updateFavorite, getFavorite
from flaskweb.search import Search
from flask_login import login_user, current_user, logout_user, login_required
from flaskweb.models import User


@app.route('/', methods=['GET', 'POST'])

@app.route('/home/', methods=['GET', 'POST'])
def home():
    form = SearchForm()
    if form.validate_on_submit():
        keyword = form.search.data
        return redirect(url_for('searchDisplay', keyword=keyword))
    return render_template('home.html', title='UmbSupport_Home', form=form)

@app.route('/about/')
def about():
    return render_template('about.html', title='About us')

@app.route('/services/<string:service_name>')
def serviceDisplay(service_name):
    data = getServices(service_name)
    if current_user.is_authenticated:
        email = current_user.email
        favoList = db.user.find_one({"email": email}).get("favorite")
    else:
        favoList=[]
    return render_template('serviceDisplay.html', title='Service Display',
                           data=data, service_name=service_name, favoList=favoList)

@app.route('/services/<service_name>/<service_id>')
@login_required
def addFavorite(service_name, service_id):
    data = getServices(service_name)
    email = current_user.email
    result = updateFavorite(email, service_name, service_id)
    if result == 'success':
        flash('You have add one favorite successfully!', 'success')
    elif result == 'fail':
        flash('You have already favorited this service.', 'info')
    if current_user.is_authenticated:
        email = current_user.email
        favoList = db.user.find_one({"email": email}).get("favorite")
    else:
        favoList=[]
    return render_template('serviceDisplay.html', title='Service Display',
                           data=data, service_name=service_name, favoList=favoList)

@app.route('/searchDisplay/<keyword>', methods=['GET', 'POST'])
def searchDisplay(keyword):
    form = SearchForm()
    data = Search(keyword)
    if current_user.is_authenticated:
        email = current_user.email
        favoList = db.user.find_one({"email": email}).get("favorite")
    else:
        favoList=[]
    if form.validate_on_submit():
        keyword = form.search.data
        return redirect(url_for('searchDisplay', keyword=keyword))
    return render_template('searchDisplay.html', title='Search Result', data=data,
                           form=form, keyword=keyword, favoList=favoList)

@app.route('/searchDisplay/<keyword>/<service_name>/<service_id>', methods=['GET', 'POST'])
@login_required
def addFavoriteSearch(keyword, service_name, service_id):
    form = SearchForm()
    data = Search(keyword)
    email = current_user.email
    result = updateFavorite(email, service_name, service_id)
    if result == 'success':
        flash('You have add one favorite successfully!', 'success')
    else:
        flash('You have already favorited this service.', 'info')
    if current_user.is_authenticated:
        email = current_user.email
        favoList = db.user.find_one({"email": email}).get("favorite")
    else:
        favoList=[]
    if form.validate_on_submit():
        keyword = form.search.data
        return redirect(url_for('searchDisplay', keyword=keyword))
    return render_template('searchDisplay.html', title='Search Result', keyword=keyword,
                           data=data, form=form, favoList=favoList)

@app.route('/services/serviceDisplay/detailedInfo/<string:servicename>/<string:service_id>',
           methods=['GET', 'POST'])
def detailedInfo(servicename, service_id):
    form = RatingForm()
    today = pass_today()
    data = getInfo(servicename, service_id)
    if form.validate_on_submit():
        if current_user.is_authenticated:
            updateRating(servicename, service_id, form.rating.data)
            flash('You have submitted rating successfully!', 'success')
            newdata = getInfo(servicename, service_id)
            return redirect(url_for('detailedInfo', servicename=servicename, service_id=service_id, data=newdata))
        else:
            flash('You should login first', 'danger')
            return redirect(url_for('login'))
    return render_template('detailedInfo.html', title='Service Imformation',
                           data=data, servicename=servicename, today=today, form=form)

@app.route("/register/", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        userjson = {'username': form.username.data, 'email':form.email.data,
                'password': hashed_pw, 'favorite': []}
        collection = db.user
        collection.insert_one(userjson)
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route("/login/", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        userjson = db.user.find_one({'email': form.email.data})
        if userjson and bcrypt.check_password_hash(userjson['password'], form.password.data):
            user = User(email=userjson['email'], username=userjson['username'])
            login_user(user, remember=form.remenber.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check username and password:)', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route("/logout/")
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route("/account/")
@login_required
def account():
    email = current_user.email
    data = getFavorite(email)
    return render_template('account.html', title='Account', data=data)



# @app.route("/search/")
# def search():
#     return render_template('', title='Account')


#