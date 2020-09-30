'''

Requirements
# pip install mysql
# pip install Flask-Mail
change the apche port to 8080 using the  following links and mysql port to 3307
1. https://stackoverflow.com/questions/10111455/i-cant-access-http-localhost-phpmyadmin
2. https://stackoverflow.com/questions/32173242/conflicting-ports-of-mysql-and-xampp
3. https://stackoverflow.com/questions/14245474/apache-wont-run-in-xampp

go to localhost:8080/phpmyadmin/

target="_blank" in layout.html to open the link in a new tab


'''
from flask import Flask 
from flask import render_template
from flask import redirect
from flask import request
from flask import session

from flask_sqlalchemy import SQLAlchemy

from flask_mail import Mail

from werkzeug.utils import secure_filename

from datetime import datetime

import json

import os

local_server = True
with open('config.json', 'r') as c:
	params = json.load(c)["params"]

app = Flask(__name__)
#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://username:password@localhost/db_name'
# when we created our databse using phpmyadmin, our user is root and password was empty, and databse name was codingthunder
#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost:3307/codingthunder'

if local_server:
	app.config['SQLALCHEMY_DATABASE_URI'] = params['local_uri']
else:
	app.config['SQLALCHEMY_DATABASE_URI'] = params['prod_uri']

# Updatin the config for Mail
# google provides an SMTP server

app.config.update(
					MAIL_SERVER = 'smtp.gmail.com',
					MAIL_PORT = '465',
					MAIL_USE_SSL = True,
					MAIL_USERNAME = params['gmail-user'],
					MAIL_PASSWORD = params['gmail-password'],	
				 )
# setting the secret key for the session
app.secret_key = 'super-secret-key'

# add the folder to app.config where we upload files
app.config['UPLOAD_FOLDER'] = params['upload_location']

mail = Mail(app)

db = SQLAlchemy(app)

# creating databse for contacts table
class Contacts(db.Model):
	'''
	sno, name, email, phone_num, msg, date
	'''
	sno = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(80), unique=False, nullable=False)
	email = db.Column(db.String(20), unique=False, nullable=False)
	phone_num = db.Column(db.String(12), unique=False, nullable=False)
	msg = db.Column(db.String(120), unique=False, nullable=False)
	date = db.Column(db.String(12), unique=False, nullable=True)

# creating databse for posts table
class Posts(db.Model):
	'''
	sno, title, slug, content, date
	'''
	sno = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(80), unique=False, nullable=False)
	tagline = db.Column(db.String(20), unique=False, nullable=False)
	slug = db.Column(db.String(21), unique=False, nullable=False)
	content = db.Column(db.String(100), unique=False, nullable=False)
	date = db.Column(db.String(12), unique=False, nullable=True)
	img_file = db.Column(db.String(20), unique=False, nullable=True)


@app.route('/')
def home():
	
	posts = Posts.query.filter_by().all()[:params['no_of_posts']]
	return render_template('index.html', params=params, posts=posts)

@app.route('/about')
def about():
	return render_template('about.html', params=params)


@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():

	if 'user' in session and session['user']==params['admin_user']:
		# means the user is already logged in
		posts = Posts.query.all()
		return render_template('dashboard.html', params=params, posts=posts)

	print(request.method)

	if request.method=='POST':
		username = request.form.get('uname')
		userpass = request.form.get('pass')
		print(username, userpass)
		if username==params['admin_user'] and userpass==params['admin_password']:
			# create a session to store the user details
			session['user'] = username
			posts = Posts.query.all()
			
			return render_template('dashboard.html', params=params, posts=posts)
	# else it is not in the page so we take it to the login.html

	return render_template('login.html', params=params)
@app.route('/edit/<string:sno>', methods=['GET', 'POST'])
def edit(sno):
	if 'user' in session and session['user']==params['admin_user']:
		if request.method=='POST':
			box_title = request.form.get('title')
			tline = request.form.get('tline')
			slug = request.form.get('slug')
			content = request.form.get('content')
			img_file = request.form.get('img_file')
			date = datetime.now()
			# if sno 0 then add new post otherwise edit old post
			if sno=='0':
				
				post = Posts(title=box_title, slug=slug, content=content, tagline=tline, img_file=img_file, date=date)
				db.session.add(post)
				db.session.commit()
			else:
				# fetch our original post
				post = Posts.query.filter_by(sno=sno).first()
				post.title = box_title
				post.tagline = tline
				post.slug = slug
				post.content = content
				post.img_file = img_file
				post.date = date
				db.session.commit()
				return redirect('/edit/'+sno)

		post = Posts.query.filter_by(sno=sno).first()
		return render_template("edit.html", params=params, post=post)


@app.route('/post/<string:post_slug>', methods=['GET'])
def post_route(post_slug):

	post = Posts.query.filter_by(slug=post_slug).first()
	return render_template('post.html', params=params, post=post)


@app.route('/contact', methods=['GET', 'POST'])
def contact():
	if request.method=='POST':
		name = request.form.get('name')
		email = request.form.get('email')
		phone = request.form.get('phone')
		message = request.form.get('message')
		date = datetime.now()
		'''
		sno, name, email, phone_num, msg, date
		'''

		entry = Contacts(name=name, email=email, phone_num=phone, msg=message, date=date)
		db.session.add(entry)
		db.session.commit()
		# before running the above insert one value manually in the database so that auto increment feature can work

		#send email
		#mail.send_message("New Message from blog " + str(name),
		#				  sender=email,
		#				  recipients=[params['gmail-user']],
		#				  body=str(message) + "\n" + str(phone))


	return render_template('contact.html', params=params)

@app.route("/uploader", methods=['GET', 'POST'])
def uploader():
	if 'user' in session and session['user']==params['admin_user']:
		if request.method=='POST':
			f = request.files['file1']
			f.save(os.path.join(app.config['UPLOAD_FOLDER']),secure_filename(f.filename))
			return "Uploaded Successfully"

@app.route("/logout", methods=['GET', 'POST'])
def logout():
	session.pop['user']
	return redirect('/dashboard')

@app.route("/delete/<string:sno>", methods=['GET', 'POST'])
def delete(sno):
	if 'user' in session and session['user']==params['admin_user']:
		post = Posts.query.filter_by(sno=sno).first()
		db.session.delete(post)
		db.session.commit()
		return redirect('/dashboard')




# vendor folder has jquery

if __name__=='__main__':
	#db.create_all()
	app.run(debug=True)