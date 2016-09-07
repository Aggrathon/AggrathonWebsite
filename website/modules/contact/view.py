from modules.contact import model
from view import render_page_standard, create_page_fromfile, try_int, create_page_admin
from app import app
from flask_login import login_required, current_user
from flask import request, url_for, flash, redirect

# frontend
@app.route('/contact/', methods=['GET', 'POST'])
def contact():
	if request.method == 'POST':
		if request.form['website'] == '':
			email = request.form['email']
			subject = request.form['subject']
			message = request.form['message']
			if email != '' and subject != '' and message != '':
				if len(email.split('@')) == 2:
					if len(email.split('@')[1].split('.')) > 1:
						if recaptcha.verify():
							model.message_add(email, subject, message)
							flash('Message sent', 'success')
							return render_page_standard(create_page_fromfile('Contact', 'modules/contact/contact.html'), True)
						else:
							flash('ReCaptcha not valid', 'error')
			return render_page_standard(create_page_fromfile('Contact', 'modules/contact/contact.html', email=email, subject=subject, message=message, check=True), True)
	return render_page_standard(create_page_fromfile('Contact', 'modules/contact/contact.html'), True)

# admin
@app.route('/admin/messages/', methods=['GET', 'POST'])
@login_required
def messages():
	if request.method == 'POST':
		action = request.form.get('action')
		if action is None:
			return 'Action not found'
		message = request.form.get('message')
		if message is None:
			return 'Invalid Message'
		if action == 'read':
			return model.message_action_read(message)
		elif action == 'unread':
			return model.message_action_unread(message)
		elif action == 'delete':
			return model.message_action_delete(message)
		elif action == 'send':
			return model.message_action_send(message)
		else:
			return 'Action not found'
	else:
		return create_page_admin('Messages', 'modules/contact/messages.html', **model.message_list(try_int(request.args.get("start"), 1) - 1, try_int(request.args.get("amount"), 20)))

@app.route('/admin/messages/blacklist/', methods=['GET', 'POST'])
@login_required
def blacklist():
	if request.method == 'POST':
		action = request.form.get('action')
		if action is None:
			return 'Action not found'
		if action == 'checkall':
			return model.message_action_recheck_all()
		phrase = request.form.get('phrase')
		if phrase is None:
			return 'Phrase not found'
		elif action == 'ban':
			return model.message_action_ban(phrase)
		elif action == 'unban':
			return model.message_action_unban(phrase)
		else:
			return 'Action not recognized'
	else:
		return create_page_admin("Message Blacklist", 'modules/contact/blacklist.html', blacklist=model.message_blacklist())

@app.route('/admin/messages/forwarding/', methods=['GET', 'POST'])
@login_required
def forwarding():
	if request.method == 'POST':
		action = request.form.get('action')
		if action:
			if action == 'remove':
				return model.message_forward_remove(request.form.get('email'))
		else:
			email = request.form.get('email')
			type = request.form.get('type')
			if email and type:
				model.message_forward_add(email, type)
	return create_page_admin("Message Forwarding", 'modules/contact/forwarding.html', forwardlist=model.message_forward_list())
	

@app.route('/admin/messages/forwarding/unsubscribe', methods=['GET'])
def forwarding_remove():
	email = request.args.get("email")
	code = request.args.get("code")
	conf = request.args.get("confirmation")
	if code and email:
		if conf:
			if model.message_forward_unsubscribe(email, code):
				flash("Forwarding Email removed", "success")
				return redirect(url_for('main'), 303)
		else:
			return render_page_standard(create_page("Unsubscribe", """
			<big>Do you wish to remove &nbsp;<em>"""+email+"""</em>&nbsp; from the forwarding list?</big><br>\n<br>\n
			<a class="btn btn-primary" href="?email="""+email+"&code="+code+"&confirmation=true\">Confirm</a>"))
	flash("Forwarding Email not recognised", "warning")
	return redirect(url_for('main'), 303)