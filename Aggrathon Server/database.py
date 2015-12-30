from flask.ext.sqlalchemy import SQLAlchemy
from app import app
from database import *
from flask_login import make_secure_token
from os import urandom
import datetime

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

	Project(id, title, content, ...)
	ProjectBlurb(project_id, description, image)
	FeaturedProject(project_id, priority)

	MORE PROJECT STUFF COMING

	Message(id, email, subject, message, time)
	MessageUnread(message_id)
	MessageBlacklist(text)
"""

###  SITE  ###

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


###  PAGES  ###

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

class PagePrivate(db.Model):
	page_id = db.Column(db.Integer, db.ForeignKey('page.id'), primary_key=True)
	page = db.relationship('Page')

	def __init__(self, page):
		self.page = page

	def __repr__(self):
		return '<Private: Page %r>' %self.page.title

class LastPage(db.Model):
	page_id = db.Column(db.Integer, db.ForeignKey('page.id'), primary_key=True)
	page = db.relationship('Page')
	time = db.Column(db.DateTime)

	def __init__(self, page):
		self.page = page
		self.time = datetime.datetime.today()
	
	def update(self):
		self.time = datetime.datetime.today()

	def __repr__(self):
		return '<Last Page: %r at %r>' %(self.page.title, self.time)


###  PROJECTS  ###

class Project(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	path = db.Column(db.Text, unique=True)
	title = db.Column(db.Text)
	text = db.Column(db.Text)
	description = db.Column(db.Text)
	thumbnail = db.Column(db.Text)

	def __init__(self, path, title, text, description, thumbnail):
		self.title = title
		self.path = path
		self.text = text
		self.description = description
		self.thumbnail = thumbnail

	def __repr__(self):
		return '<Project %r>' %self.title
	
class ProjectImage(db.Model):
	project_id = db.Column(db.Integer, db.ForeignKey('project.id'), primary_key=True)
	project = db.relationship('Project')
	image = db.Column(db.Text, primary_key=True)
	number = db.Column(db.Integer)

	def __init__(self, project, image, number=0):
		self.project = project
		self.image = image
		self.number = number

	def __repr__(self):
		return '<Project %r Image: %r>' %(self.project.title, self.image)

class ProjectLink(db.Model):
	project_id = db.Column(db.Integer, db.ForeignKey('project.id'), primary_key=True)
	project = db.relationship('Project')
	link = db.Column(db.Text, primary_key=True)
	number = db.Column(db.Integer)
	
	def __init__(self, project, link, number=0):
		self.project = project
		self.link = link
		self.number = number

	def __repr__(self):
		return '<Project %r Link: %r>' %(self.project.title, self.link)

class ProjectVersion(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
	project = db.relationship('Project')
	major = db.Column(db.Integer)
	minor = db.Column(db.Integer)
	patch = db.Column(db.Integer)
	changelog = db.Column(db.Text)
	files = db.relationship("ProjectFile", back_populates="version")
	__table_args__ = (None, db.UniqueConstraint('project_id', 'major', 'minor', 'patch', name='project_version_unique') )
	
	def __init__(self, project, major=1, minor=0, patch=0, changelog=""):
		self.project = project
		self.major = major
		self.minor = minor
		self.patch = patch
		self.changelog = changelog

	def __repr__(self):
		return '<Project %r Version: %r.%r.%r>' %(self.project.title, self.major, self.minor, self.patch)

class ProjectFile(db.Model):	
	version_id = db.Column(db.Integer, db.ForeignKey('project_version.id'), primary_key=True)
	version = db.relationship('ProjectVersion', back_populates="files")
	title = db.Column(db.Text, primary_key=True)
	url = db.Column(db.Text)
	
	def __init__(self, version, title, url):
		self.version = version
		self.title = title
		self.url = url
		
	def __repr__(self):
		return '<Project %r (%r.%r.%r) File: %r>' %(self.version.project.title, self.version.major, self.version.minor, self.version.patch, self.title)

class FeaturedProject(db.Model):
	project_id = db.Column(db.Integer, db.ForeignKey('project.id'), primary_key=True)
	project = db.relationship('Project')
	priority = db.Column(db.Integer)

	def __init__(self, project, priority=0):
		self.project = project
		self.priority = priority

	def __repr__(self):
		return '<Featured: Project %r>' %self.project.title

class LastProject(db.Model):
	project_id = db.Column(db.Integer, db.ForeignKey('project.id'), primary_key=True)
	project = db.relationship('Project')
	time = db.Column(db.DateTime)

	def __init__(self, project):
		self.project = project
		self.time = datetime.datetime.today()

	def update(self):
		self.time = datetime.datetime.today()

	def __repr__(self):
		return '<Last Project: %r at %r>' %(self.page.name, self.time)


###  MESSAGES  ###

class Message(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	email = db.Column(db.Text)
	subject = db.Column(db.Text)
	message = db.Column(db.Text)
	time = db.Column(db.DateTime)
	
	def __init__(self, email, subject, message):
		self.email = email
		self.subject = subject
		self.message = message
		self.time = datetime.datetime.today()
		
	def __repr__(self):
		return '<Message: %r from %r>' %(self.subject, self.email)

class MessageUnread(db.Model):
	message_id = db.Column(db.Integer, db.ForeignKey('message.id'), primary_key=True)
	message = db.relationship('Message')

	def __init__(self, message):
		self.message = message
	
	def __repr__(self):
		return '<Unread Message: %r from %r>' %(self.message.subject, self.message.email)

class MessageBlacklist(db.Model):
	text = db.Column(db.Text, primary_key=True)

	def __init__(self, text):
		self.text = text.casefold()

	def check_message(message):
		message = message.casefold()
		for phrase in MessageBlacklist.query.all():
			if message.find(phrase.text) != 0:
				return False
		return True

	def __repr__(self):
		return '<Blacklisted Phrase: %r>' %self.text

class MessageForwarding(db.Model):
	email = db.Column(db.Text, primary_key=True)
	type = db.Column(db.Integer)
	code = db.Column(db.Text)

	def __init__(self, email, type, code):
		self.email = email
		self.type = type
		self.code = code

	def __repr__(self):
		return '<Message Forwarding Email: %r>' %self.email


### USER ###

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

### SETUP ####

def create_db():
	db.create_all()
	db.session.commit()
	session = SQLAlchemy.create_scoped_session(db)
	session.add(Site(app.config['WEBSITE_NAME'], app.config['WEBSITE_HEADER'], app.config['WEBSITE_LANGUAGE']))
	for item in app.config['WEBSITE_MENU']:
		session.add(Menu(item['title'], item['target'] ))
	for user in app.config['WEBSITE_ADMIN']:
		session.add(User(user))
	session.add( Page('/', '', 'This is the main page') )
	session.commit();

def reset_db():
	try:
		for user in User.query.all():
			if user.email not in app.config['WEBSITE_ADMIN']:
				app.config['WEBSITE_ADMIN'].append(user.email)
	except:
		pass
	db.drop_all()
	create_db()

def check_if_setup():
	try:
		if(Site.query.first() is None):
			raise Exception ("Site information not found")
		Menu.query.first()
		Text.query.first()

		Page.query.first()
		PageBlurb.query.first()
		FeaturedPage.query.first()
		PagePrivate.query.first()
		LastPage.query.first()

		Project.query.first()
		ProjectImage.query.first()
		ProjectLink.query.first()
		ProjectVersion.query.first()
		ProjectFile.query.first()
		FeaturedProject.query.first()
		LastProject.query.first()

		MessageBlacklist.query.first()
		MessageUnread.query.first()
		Message.query.first()
		MessageForwarding.query.first();

		User.query.first()
	except Exception as e:
		print('\033[93m'+format(e)+'\033[0m')
		return False
	return True