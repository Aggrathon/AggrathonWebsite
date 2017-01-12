from database import db

class PageImage(db.Model):
	page_id = db.Column(db.Integer, db.ForeignKey('page.id'), primary_key=True)
	page = db.relationship('Page')
	image = db.Column(db.Text)
	index = db.Column(db.Integer)
	
	def __init__(self, page, image="", index=0):
		self.page = page
		self.index = index
		self.image = image

	def __repr__(self):
		return '<Page Image: %r %r>' % (self.page.title, self.image)


def add_images_to_data(data):
	pass

def save_images(data):
	pass

def setup():
	PageImage.query.first()
