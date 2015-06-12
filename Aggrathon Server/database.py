from flask.ext.sqlalchemy import SQLAlchemy
from app import app
db = SQLAlchemy(app)


class Page(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	path = db.Column(db.Text, unique=True)
	title = db.Column(db.Text)
	content = db.Column(db.Text)
	description = db.Column(db.Text)

	def __init__(self, path, title, content, description):
		self.title = title
		self.path = path
		self.content = content
		self.description = description

	def __repr__(self):
		return '<Page %r>' %self.title

class Menu(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.Text)
	target = db.Column(db.Text)

	def __init__(self, title, target):
		self.title = title
		self.target = target

	def __repr__(self):
		return '<Menuitem %r>' %self.title

class FeaturedPage(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	page_id = db.Column(db.Integer, db.ForeignKey('page.id'))
	page = db.relationship('Page')

	def __init__(self, page):
		self.page = page

	def __repr__(self):
		return '<Featured Page %r>' %self.page.title

#Still only a copy of featured page
class FeaturedProject(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	page_id = db.Column(db.Integer, db.ForeignKey('page.id'))
	page = db.relationship('Page')

	def __init__(self, page):
		self.page = page

	def __repr__(self):
		return '<Featured Page %r>' %self.page.title
