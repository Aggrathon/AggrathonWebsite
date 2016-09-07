from modules.contact.database import *
from database import db
from flask import abort, flash, url_for
from model import RETURN_SUCCESS, FLASH_SUCCESS, FLASH_WARNING, FLASH_ERROR, get_random_code, email_send_text, email_send_html

#region MESSAGES

def message_add(email, subject, message):
	if MessageBlacklist.check_message(email):
		if MessageBlacklist.check_message(subject):
			if MessageBlacklist.check_message(message):
				mess = Message(email, subject, message)
				unr = MessageUnread(mess)
				db.session.add(mess)
				db.session.add(unr)
				db.session.commit()
				message_forward(mess)
				return RETURN_SUCCESS
	return 'blocked'

def message_unread_count():
	return MessageUnread.query.count()

def message_total_count():
	return Message.query.count()

def message_admin_button():
	unread = message_unread_count()
	button = """
		<a href="/admin/messages/" class="btn btn-default" title="Messages">
			<span class="glyphicon glyphicon-envelope" aria-hidden="true"></span>
			<span class="sr-only">Messages, %s unread</span>
	""" %unread
	if unread > 0:
		button = button + '\n<span class="badge" aria-hidden="true">%s</span>' %unread
	return button + '\n</a>'

def message_list(start=0, amount=20):
	total = message_total_count()
	if start >= total:
		start = total - amount
	if start < 0:
		start = 0
	list = db.session.query(
		Message.id.label('id'), Message.email.label('email'), Message.subject.label('subject'), Message.message.label('message'),
		MessageUnread.message_id.label('unread'), Message.time.label('time')).outerjoin(MessageUnread).order_by(Message.id.desc()).offset(start).limit(amount).all()
	return {'messages':list, 'start':start+1, 'amount':amount, 'total':total}

def message_blacklist():
	return MessageBlacklist.query.all();

#endregion

#region MESSAGES_ACTIONS

def message_action_unread(id):
	mess = Message.query.get(id)
	if mess is not None:
		if MessageUnread.query.get(id) is None:
			db.session.add(MessageUnread(mess))
			db.session.commit()
		return RETURN_SUCCESS
	return 'Message not found'

def message_action_read(id):
	unr = MessageUnread.query.get(id)
	if unr is not None:
		db.session.delete(unr)
		db.session.commit()
	return RETURN_SUCCESS

def message_action_delete(id):
	mess = Message.query.get(id)
	if mess is not None:
		unr = MessageUnread.query.get(id)
		if unr is not None:
			db.session.delete(unr)
		db.session.delete(mess)
		db.session.commit()
		return RETURN_SUCCESS
	return 'Message not found'

def message_action_ban(phrase):
	mb = MessageBlacklist.query.get(phrase.casefold())
	if mb is None:
		db.session.add(MessageBlacklist(phrase))
		db.session.commit()
		return RETURN_SUCCESS
	return "Phrase already banned"

def message_action_unban(phrase):
	mb = MessageBlacklist.query.get(phrase.casefold())
	if mb is not None:
		db.session.delete(mb)
		db.session.commit()
		return RETURN_SUCCESS
	return 'Phrase not found'

def message_action_recheck_all():
	removed = 0
	messages = Message.query.all()
	bl = MessageBlacklist.query.all()
	for mess in messages:
		email = mess.email.casefold()
		subject = mess.subject.casefold()
		message = mess.message.casefold()
		for b in bl:
			if email.find(b.text) != -1:
				message_action_delete(mess.id)
				removed += 1
				break
			if subject.find(b.text) != -1:
				message_action_delete(mess.id)
				removed += 1
				break
			if message.find(b.text) != -1:
				message_action_delete(mess.id)
				removed += 1
				break
	if removed is 1:
		return '1 Message deleted'
	return '%s Messages deleted' %removed

def message_action_send(id):
	mess = Message.query.get(id)
	if mess is not None:
		email_send_text(mess.subject, current_user.email, mess.message, mess.email)
		return RETURN_SUCCESS
	return 'Message not found'


def message_forward_add(email, type):
	forw = MessageForwarding.query.get(email)
	if forw is None:
		code = get_random_code()
		forw = MessageForwarding(email, type, code)
		db.session.add(forw)
		db.session.commit()
		url = url_for('forwarding_remove', email=email, code=code, _external=True)
		email_send_html(get_site_info()['name']+" - Message Forwarding Confirmation", email, """
		This email has been setup to recieve notifications on messages sent to the site\n<br />
		Click here to unsubscribe: <a href=\""""+url+"\">"+url+"</a>\n<br />")
		flash("Forwarding Email added ("+email+")", FLASH_SUCCESS)
	else:
		forw.type = type
		db.session.commit()
		flash("Forwarding settings changed for "+email, FLASH_SUCCESS)

def message_forward_remove(email):
	forw = MessageForwarding.query.get(email)
	if forw is not None:
		db.session.delete(forw)
		db.session.commit()
		return RETURN_SUCCESS
	return "Email not found ("+email+")"

def message_forward_unsubscribe(email, code):
	forw = MessageForwarding.query.get(email)
	if forw is not None:
		if forw.code == code:
			db.session.delete(forw)
			db.session.commit()
			return True
	return False

def message_forward_list():
	return db.session.query(MessageForwarding.email, MessageForwarding.type)

def message_forward(message):
	unr = message_unread_count()
	frwds = MessageForwarding.query.all()
	one = unr == 1
	remind = one or (unr == 5 or (unr < 100 and unr%10 == 0) or unr%100 == 0)
	for frw in frwds:
		if frw.type == 0:
			email_send_text(message.subject, frw.email, message.message, message.email)
		elif (frw.type == 1 and remind) or (frw.type == 2 and one):
			url = url_for('messages', _external=True)
			url2 = url_for('forwarding_remove', email=frw.email, code=frw.code, _external=True)
			email_send_html(get_site_info()['name']+" - Unread messages: "+str(unr), frw.email, """
			This email has been setup to recieve notifications on messages sent to the site\n<br />\n<br />
			You have """+str(unr)+""" unread messages\n<br />
			Click here to read them: <a href=\""""+url+"\">"+url+"""</a>\n<br />\n<br />\n<br />
			Click here to unsubscribe: <a href=\""""+url2+"\">"+url2+"</a>\n<br />")

#endregion

def create_test_data():
	message_add("example@not.real", "Test Content", "Remember to remove all test-content on a real site")