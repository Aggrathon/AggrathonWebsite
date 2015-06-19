from flask.ext.sqlalchemy import SQLAlchemy
from app import app
from flask import abort

db = SQLAlchemy(app)

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

def getFeaturedPages():
	pages = db.session.query(
		Page.path.label('url'), PageBlurb.description.label('description'), Page.title.label('title'), PageBlurb.image.label('img'))\
		.join(FeaturedPage).filter(FeaturedPage.page_id==Page.id).join(PageBlurb).filter(PageBlurb.page_id==Page.id)\
		.order_by(FeaturedPage.priority).all()
	return pages

def getFeaturedProjects():
	projects = db.session.query(
		Project.path.label('url'), ProjectBlurb.description.label('description'), Project.title.label('title'), ProjectBlurb.image.label('img'))\
		.join(FeaturedProject).filter(FeaturedProject.project_id==Project.id).join(ProjectBlurb).filter(ProjectBlurb.project_id==Project.id)\
		.order_by(FeaturedProject.priority).all()
	return projects

def getStats():
	pages = Page.query.count()
	projects = Project.query.count()
	return {'pages':pages, 'projects':projects}


### SETTERS ###

def setMenu(menu):
	oldmenu = Menu.query.all()
	curr = 0
	while( curr < len(oldmenu) and curr < len(menu) ):
		oldmenu[curr].title = menu[curr]['title']
		oldmenu[curr].target = menu[curr]['target']
		curr += 1
	while(curr < len(menu)):
		db.session.add(Menu(menu[curr]['title'], menu[curr]['target']))
		curr += 1
	while(curr < len(oldmenu)):
		db.session.delete(oldmenu[curr])
		curr += 1
	db.session.commit()
	
def setPage(path, title, content, featured=False, priority=0, description="", thumbnail=""):
	page = Page.query.filter_by(path="/pages/test/").first()
	if(page is None):
		page = Page(path, title, content)
		db.session.add(page)
		if(featured):
			db.session.add( FeaturedPage(page, priority) )
			db.session.add( PageBlurb(page, description, thumbnail) )
		elif(description != "" or thumbnail != ""):
			db.session.add( PageBlurb(page, description, thumbnail) )
	else:
		page.path = path
		page.title = title
		page.content = content

		if(featured):
			feature = FeaturedPage.query.get(page.id)
			if(feature is None):
				db.session.add( FeaturedPage(page, priority) )
			else:
				feature.priority = priority
		else:
			feature = FeaturedPage.query.get(page.id)
			if(feature is not None):
				db.session.delete(feature)

		desc = description != ""
		thumb = thumbnail != ""
		blurb = PageBlurb.query.get(page.id)
		if(blurb is None):
			if(desc or thumb or featured):
				db.session.add( PageBlurb(page, description, thumbnail) )
		else:
			if(not desc and not thumb):
				db.session.delete(blurb)
			else:
				blurb.description = description
				blurb.image = thumbnail

	db.session.commit()

def createTestData():
	page = Page("/pages/test/", "Test Page 1", "[insert content here]")
	db.session.add(page)
	db.session.add(Page("/pages/test2/", "Test Page 2", "[insert content here]"))
	db.session.add(Page("/pages/test3/", "Test Page 3", "[insert content here]"))
	db.session.add(FeaturedPage(page, 10))
	db.session.add(PageBlurb(page, "Description for test page 1", "/static/background.jpg"))

	db.session.add(Menu("Home","/"))
	db.session.add(Menu("Stuff","/stuff/"))
	db.session.add(Menu("Admin","/admin/"))
	db.session.add(Menu("Projects","/projects/"))
	
	proj = Project("/projects/test/", "Test Project 1", "[insert content here]")
	db.session.add(FeaturedProject(proj, 10))
	db.session.add(ProjectBlurb(proj, "Test Project 1 description here", ""))

	db.session.commit();


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
