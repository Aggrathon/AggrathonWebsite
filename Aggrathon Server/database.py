from flask.ext.sqlalchemy import SQLAlchemy
from app import app
from database import *

db = SQLAlchemy(app)

### TABLES ###
"""
	Database scheme:

	Site(name, header, language)
	Menu(id, title, target)

	Page(id, path, title, content)
	PageBlurb(page_id, description, image)
	FeaturedPage(page_id, priority)

	Project(id, title, content, ...)
	ProjectBlurb(project_id, description, image)
	FeaturedProject(project_id, priority)

	MORE PROJECT STUFF COMING
"""

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



class Page(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	path = db.Column(db.Text, unique=True)
	title = db.Column(db.Text)
	content = db.Column(db.Text)

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



class Project(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	path = db.Column(db.Text, unique=True)
	title = db.Column(db.Text)
	content = db.Column(db.Text)

	def __init__(self, path, title, content):
		self.title = title
		self.path = path
		self.content = content

	def __repr__(self):
		return '<Project %r>' %self.title

class ProjectBlurb(db.Model):
	project_id = db.Column(db.Integer, db.ForeignKey('project.id'), primary_key=True)
	project = db.relationship('Project')
	description = db.Column(db.Text)
	image = db.Column(db.Text)

	def __init__(self, project, description, image=""):
		self.project = project
		self.description = description
		self.image = image

	def __repr__(self):
		return '<Blurb: Project %r>' %self.project.title

class FeaturedProject(db.Model):
	project_id = db.Column(db.Integer, db.ForeignKey('project.id'), primary_key=True)
	project = db.relationship('Project')
	priority = db.Column(db.Integer)

	def __init__(self, project, priority=0):
		self.project = project
		self.priority = priority

	def __repr__(self):
		return '<Featured: Project %r>' %self.project.title

class MessageBlacklist(db.Model):
	text = db.Column(db.Text, primary_key=True)
	def __init__(self, text):
		self.text = text

	def __repr__(self):
		return '<Blacklist: %r>' %self.text

class Message(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	email = db.Column(db.Text)
	subject = db.Column(db.Text)
	message = db.Column(db.Text)
	
	def __init__(self, email, subject, message):
		self.email = email
		self.subject = subject
		self.message = message
		
	def __repr__(self):
		return '<Message: %r from %r>' %(self.subject, self.email)

class MessageUnread(db.Model):
	message_id = db.Column(db.Integer, db.ForeignKey('message.id'), primary_key=True)
	message = db.relationship('Message')

	def __init__(self, message):
		self.message = message

	def __repr__(self):
		return '<Unread Message: %r from %r>' %(self.message.subject, self.message.email)


### SETUP ####

def create_db():
	db.create_all()
	setup()

def reset_db():
	db.drop_all()
	create_db()

def check_if_setup():
	try:
		if(Site.query.first() is None):
			raise Exception
		Menu.query.first()

		Page.query.first()
		PageBlurb.query.first()
		FeaturedPage.query.first()

		Project.query.first()
		ProjectBlurb.query.first()
		FeaturedProject.query.first()

		MessageBlacklist.query.first()
		MessageUnread.query.first()
		Message.query.first()
	except:
		return False
	return True

def setup(name="Website", header="Website", language="en"):
	site = Site.query.first()
	if(site is None):
		site = Site(name, header, language)
		db.session.add(site)
	else:
		site.name = name
		site.header = header
		site.language = language
	if(Page.query.filter_by(path = '/').first() is None):
		db.session.add( Page('/', '', 'This is the main page') )
	db.session.commit()