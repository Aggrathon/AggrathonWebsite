from flask.ext.sqlalchemy import SQLAlchemy
from app import app
from flask import abort

db = SQLAlchemy(app)

### SETUP ####

def create_db(siteName="Website", siteHeader="Website", siteLanguage="en"):
	db.create_all()
	setup(siteName, siteHeader, siteLanguage)

def reset_db():
	db.drop_all()
	create_db()

def setup(name, header, language):
	site = Site.query.first()
	if(site is None):
		site = Site(name, header, language)
		db.session.add(site)
	else:
		site.name = name
		site.header = header
		site.language = language
	db.session.commit()

def check_setup():
	try:
		Site.query.first()
		Menu.query.first()

		Page.query.first()
		PageBlurb.query.first()
		FeaturedPage.query.first()

		Project.query.first()
		ProjectBlurb.query.first()
		FeaturedProject.query.first()
	except:
		return False
	return True


### GETTERS ###

def getMenu():
	return Menu.query.all()

def getSiteInfo():
	site = Site.query.first()
	if(site is None):
		abort(500)
	return {'name':site.name, 'header':site.header, 'language':site.language, 'menu':getMenu()}

def getPage(path):
	page = Page.query.filter_by(path=path).first()
	if(page is None):
		abort(404)
	return page

"""
url: link target
		img: url to thumbnail
		title: header
		description: short text describing the item
"""
def getFeaturedPages():
	pages = db.session.query(
		Page.path.label('url'), PageBlurb.description.label('description'), Page.title.label('title'), PageBlurb.image.label('img'))\
		.join(FeaturedPage).filter(FeaturedPage.page_id==Page.id).join(PageBlurb).filter(PageBlurb.page_id==Page.id)\
		.order_by(FeaturedPage.priority).all()
	return pages


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

	def __init__(self, page, description, image):
		self.page = page
		self.description = description
		self.image = image

	def __repr__(self):
		return '<Blurb: Page %r>' %self.page.title

class FeaturedPage(db.Model):
	page_id = db.Column(db.Integer, db.ForeignKey('page.id'), primary_key=True)
	page = db.relationship('Page')
	priority = db.Column(db.Integer)

	def __init__(self, page, priority):
		self.page = page
		self.priority = priority

	def __repr__(self):
		return '<Featured: Page %r>' %self.page.title



class Project(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.Text)
	content = db.Column(db.Text)

	def __init__(self, title, content, description):
		self.title = title
		self.content = content
		self.description = description

	def __repr__(self):
		return '<Project %r>' %self.title

class ProjectBlurb(db.Model):
	project_id = db.Column(db.Integer, db.ForeignKey('project.id'), primary_key=True)
	project = db.relationship('Project')
	description = db.Column(db.Text)
	image = db.Column(db.Text)

	def __init__(self, project, description, image):
		self.project = project
		self.description = description
		self.image = image

	def __repr__(self):
		return '<Blurb: Project %r>' %self.project.title

class FeaturedProject(db.Model):
	project_id = db.Column(db.Integer, db.ForeignKey('project.id'), primary_key=True)
	project = db.relationship('Project')
	priority = db.Column(db.Integer)

	def __init__(self, project, priority):
		self.project = project
		self.priority = priority

	def __repr__(self):
		return '<Featured: Project %r>' %self.project.title
