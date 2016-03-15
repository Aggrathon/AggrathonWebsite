from database import db
import datetime

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

def check_setup():
	MessageBlacklist.query.first()
	MessageUnread.query.first()
	Message.query.first()
	MessageForwarding.query.first();