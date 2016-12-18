from flask.ext.sqlalchemy import SQLAlchemy
from app import app
from sqlalchemy.orm import relationship
from database import db
import datetime
import os

"""
	Database scheme:
	
		Project
		ProjectImage
		ProjectLink
		ProjectVersion
		ProjectFile
		ProjectTag
		ProjectTagged
		ProjectFeatured
		ProjectLast
"""

class Project(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	path = db.Column(db.Text, unique=True)
	title = db.Column(db.Text)
	text = db.Column(db.Text)
	description = db.Column(db.Text)
	thumbnail = db.Column(db.Text)
	images = db.relationship("ProjectImage", back_populates="project")
	links = db.relationship("ProjectLink", back_populates="project")
	versions = db.relationship("ProjectVersion", back_populates="project")
	tags = db.relationship("ProjectTagged", back_populates="project")
	created = db.Column(db.DateTime)
	edited = db.Column(db.DateTime)
	

	def __init__(self, path, title, text, description, thumbnail):
		self.title = title
		self.path = path
		self.text = text
		self.description = description
		self.thumbnail = thumbnail
		today =  datetime.datetime.today()
		self.created = today
		self.edited = today
		
	def get_latest_version(self):
		return ProjectVersion.query.filter_by(project=self).order_by(ProjectVersion.major.desc(),ProjectVersion.minor.desc(),ProjectVersion.patch.desc()).first()

	def set_edited(self):
		self.edited = datetime.datetime.today()
		ProjectLast.update(self)

	def __repr__(self):
		return '<Project %r>' %self.title
	
class ProjectImage(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
	project = db.relationship('Project', back_populates="images")
	image = db.Column(db.Text)

	def __init__(self, project, image):
		self.project = project
		self.image = image

	def __repr__(self):
		return '<Project %r Image: %r>' %(self.project.title, self.image)

class ProjectLink(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
	project = db.relationship('Project', back_populates="links")
	link = db.Column(db.Text)
	title = db.Column(db.Text)
	
	def __init__(self, project, title, link):
		self.project = project
		self.title = title
		self.link = link

	def __repr__(self):
		return '<Project %r Link: %r>' %(self.project.title, self.link)

class ProjectVersion(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
	project = db.relationship('Project', back_populates="versions")
	major = db.Column(db.Integer)
	minor = db.Column(db.Integer)
	patch = db.Column(db.Integer)
	changelog = db.Column(db.Text)
	date = db.Column(db.Date)
	files = db.relationship("ProjectFile", back_populates="version")
	__table_args__ = (None, db.UniqueConstraint('project_id', 'major', 'minor', 'patch', name='project_version_unique') )
	
	def __init__(self, project, major=1, minor=0, patch=0, changelog="", date=None):
		self.project = project
		self.major = major
		self.minor = minor
		self.patch = patch
		self.changelog = changelog
		if date is None:
			self.date = datetime.date.today()
		elif type(date) == str:
			if not self.set_date(date):
				self.date = datetime.date.today()
		else:
			self.date = date

	def set_date(self, iso_date):
		try:
			d = datetime.datetime.strptime(iso_date, "%Y-%m-%d")
			self.date = d.date()
			return True
		except ValueError:
			return False
	
	def get_version(self):
		ver = str(self.major)
		if(self.minor is not 0 or self.patch is not 0):
			ver += ".%d" %self.minor
		if(self.patch != 0):
			ver += ".%d" %self.patch
		return ver

	def __repr__(self):
		return '<Project %r Version: %r.%r.%r>' %(self.project.title, self.major, self.minor, self.patch)

class ProjectFile(db.Model):	
	id = db.Column(db.Integer, primary_key=True)
	version_id = db.Column(db.Integer, db.ForeignKey('project_version.id'))
	version = db.relationship('ProjectVersion', back_populates="files")
	title = db.Column(db.Text)
	url = db.Column(db.Text)
	
	
	def __init__(self, version, title, url):
		self.version = version
		self.title = title
		self.url = url
		
	def __repr__(self):
		return '<Project %r (%d.%d.%d) File: %r>' %(self.version.project.title, self.version.major, self.version.minor, self.version.patch, self.title)

class ProjectTag(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	tag = db.Column(db.String, unique=True)
	projects = db.relationship('ProjectTagged', back_populates="tag")
	
	def __init__(self, tag):
		self.tag = tag
		
	def __repr__(self):
		return '<Tag: %r>' %self.tag
	
class ProjectTagged(db.Model):
	tag_id = db.Column(db.Integer, db.ForeignKey('project_tag.id'), primary_key=True)
	tag =  db.relationship("ProjectTag", back_populates="projects")
	project_id = db.Column(db.Integer, db.ForeignKey('project.id'), primary_key=True)
	project = db.relationship("Project", back_populates="tags")
	
	def __init__(self, project, tag):
		self.tag = tag
		self.project = project
	
	def __repr__(self):
		return "<Project Tag: '%r' '%r'>" %(self.project.title, self.tag.tag)
	
	
class ProjectFeatured(db.Model):
	project_id = db.Column(db.Integer, db.ForeignKey('project.id'), primary_key=True)
	project = db.relationship('Project')
	priority = db.Column(db.Integer)

	def __init__(self, project, priority=0):
		self.project = project
		self.priority = priority

	def __repr__(self):
		return '<Featured: Project %r>' %self.project.title

class ProjectLast(db.Model):
	project_id = db.Column(db.Integer, db.ForeignKey('project.id'), primary_key=True)
	project = db.relationship('Project')
	time = db.Column(db.DateTime)

	def __init__(self, project):
		self.project = project
		self.time = datetime.datetime.today()
		if ProjectLast.query.count() >= 5:
			db.session.delete(ProjectLast.query.order_by('time').first())

	def update(project):
		last = ProjectLast.query.get(project.id)
		if last is None:
			db.session.add(ProjectLast(project))
		else:
			last.time = datetime.datetime.today()
		db.session.commit()

	def __repr__(self):
		return '<Last Project: %r at %r>' %(self.page.name, self.time)

def setup():
	Project.query.first()
	ProjectImage.query.first()
	ProjectLink.query.first()
	ProjectVersion.query.first()
	ProjectFile.query.first()
	ProjectTag.query.first()
	ProjectTagged.query.first()
	ProjectFeatured.query.first()
	ProjectLast.query.first()
	os.makedirs(os.path.join('files','projects'), exist_ok=True)