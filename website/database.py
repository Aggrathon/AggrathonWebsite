from flask.ext.sqlalchemy import SQLAlchemy
from app import app, get_hook, HOOK_DATABASE_CREATE, HOOK_DATABASE_RESET, HOOK_DATABASE_SETUP_CHECK
from flask import url_for
from database import *
from flask_login import make_secure_token
from os import urandom
import datetime
from sqlalchemy.orm import relationship

db = SQLAlchemy(app)

### TABLES ###
"""
	Database scheme:

	Site(name, header, language)
	Menu(id, title, target)

	Page(id, path, title, content)
	PageBlurb(page_id, description, image)
	FeaturedPage(page_id, priority)
	PagePrivate(page_id)
"""

#region SITE

class Site(db.Model):
	name = db.Column(db.Text, primary_key=True)
	header = db.Column(db.Text)
	language = db.Column(db.String(8))

	def __init__(self, name, header, language):
		self.name = name
		self.header = header
		self.language = language

	def __repr__(self):
		return '<Site %r>' %self.name

class Menu(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.Text)
	target = db.Column(db.Text)

	def __init__(self, title, target):
		self.title = title
		self.target = target

	def __repr__(self):
		return '<Menuitem %r>' %self.title

class Text(db.Model):
	id = db.Column(db.String(12, None, True), primary_key=True)
	text = db.Column(db.Text)

	def __init__(self, id, text):
		self.id = id
		self.text = text

	def __repr__(self):
		return '<Text %r>' %self.id

#endregion

#region PAGES

class Page(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	path = db.Column(db.Text, unique=True)
	title = db.Column(db.Text)
	content = db.Column(db.Text)

	@property
	def url(self):
		return url_for("page", self.path)

	def __init__(self, path, title, content):
		self.title = title
		self.path = path
		self.content = content

	def __repr__(self):
		return '<Page %r>' %self.title

class PageBlurb(db.Model):
	page_id = db.Column(db.Integer, db.ForeignKey('page.id'), primary_key=True)
	page = db.relationship('Page')
	description = db.Column(db.Text)
	image = db.Column(db.Text)

	def __init__(self, page, description, image=""):
		self.page = page
		self.description = description
		self.image = image

	def __repr__(self):
		return '<Blurb: Page %r>' %self.page.title

class FeaturedPage(db.Model):
	page_id = db.Column(db.Integer, db.ForeignKey('page.id'), primary_key=True)
	page = db.relationship('Page')
	priority = db.Column(db.Integer)

	def __init__(self, page, priority=0):
		self.page = page
		self.priority = priority

	def __repr__(self):
		return '<Featured: Page %r>' %self.page.title

class PagePrivate(db.Model):
	page_id = db.Column(db.Integer, db.ForeignKey('page.id'), primary_key=True)
	page = db.relationship('Page')

	def __init__(self, page):
		self.page = page

	def __repr__(self):
		return '<Private: Page %r>' %self.page.title

class PageLast(db.Model):
	page_id = db.Column(db.Integer, db.ForeignKey('page.id'), primary_key=True)
	page = db.relationship('Page')
	time = db.Column(db.DateTime)

	def __init__(self, page):
		self.page = page
		self.time = datetime.datetime.today()
		if PageLast.query.count() >= 5:
			db.session.delete(PageLast.query.order_by('time').first())
	
	def update(page):
		last = PageLast.query.filter_by(page_id=page.id).first()
		if last is None:
			db.session.add(PageLast(page))
		else:
			last.time = datetime.datetime.today()
		db.session.commit()

	def __repr__(self):
		return '<Last Page: %r at %r>' %(self.page.title, self.time)

#endregion

#region USER

class User(db.Model):
	email = db.Column(db.Text, primary_key=True)
	token = db.Column(db.Text, unique=True)

	verification_time = db.Column(db.DateTime)
	verification_code = db.Column(db.Text)

	def is_active(self):
		return True
	def is_authenticated(self):
		return True
	def is_anonymous(self):
		return False
	def get_id(self):
		return self.email
	def get_auth_token(self):
		return self.token

	def get_verification_expired(self):
		if self.verification_time:
			return (datetime.datetime.today() - self.verification_time).total_seconds() > 300
		else:
			return True

	def set_verification(self, code):
		self.verification_code = code
		self.verification_time = datetime.datetime.today()
		db.session.commit()

	def __init__(self, email):
		rand = urandom(16)
		token = make_secure_token(email, key=rand)
		while User.query.filter_by(token=token).first() is not None:
			rand = urandom(16)
			token = make_secure_token(email, rand)
		self.email = email
		self.token = token

	def __repr__(self):
		return '<User: %r>' %self.email

	def __eq__(self, other):
		if isinstance(other, User):
			return self.email == other.email
		return False

	def __ne__(self, other):
		return not self.__eq__(other)

#endregion

#region SETUP

def setup_db():
	try:
		for dbf in get_hook(HOOK_DATABASE_SETUP_CHECK):
			dbf()
	except Exception as e:
		print('\033[93m'+format(e)+'\033[0m')
		if app.config['DATABASE_SCHEMA_ERROR_ACTION'] == 'NOTHING':
			print('\033[93m'+"The Database Schema doesn't match the website, check the database or use the 'Reset Database' function (in /admin/setup/) to remove old data"+'\033[0m')
		else:
			reset_db()
			print('\033[93m'+"The Database has been reset due to not matching the website"+'\033[0m')

def create_db():
	db.create_all()
	db.session.commit()
	session = SQLAlchemy.create_scoped_session(db)
	for dbf in get_hook(HOOK_DATABASE_CREATE):
		dbf(session)
	session.commit();

def reset_db():
	for dbf in get_hook(HOOK_DATABASE_RESET):
		dbf()
	db.drop_all()
	create_db()

#endregion

#region SETUP SELF

def setup_self():
	if(Site.query.first() is None):
		raise Exception ("Site information not found")
	Menu.query.first()
	Text.query.first()

	Page.query.first()
	PageBlurb.query.first()
	FeaturedPage.query.first()
	PagePrivate.query.first()
	PageLast.query.count()

	User.query.first()

def create_self(session):
	session.add(Site(app.config['WEBSITE_NAME'], app.config['WEBSITE_HEADER'], app.config['WEBSITE_LANGUAGE']))
	for item in app.config['WEBSITE_MENU']:
		session.add(Menu(item['title'], item['target'] ))
	for user in app.config['WEBSITE_ADMIN']:
		session.add(User(user))
	session.add( Page('/', '', 'This is the main page') )

def reset_self():
	try:
		for user in User.query.all():
			if user.email not in app.config['WEBSITE_ADMIN']:
				app.config['WEBSITE_ADMIN'].append(user.email)
	except:
		pass

#endregion