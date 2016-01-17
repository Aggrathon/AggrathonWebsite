from flask import Flask, request, flash, redirect, url_for, jsonify, send_from_directory
from app import app, login_manager, recaptcha
from flask_login import login_user, logout_user, login_required, current_user
from view import *
import model

### ROUTES ###

### main ###
@app.route('/')
def main():
	return show_page('/')

### admin ###
@app.route('/admin/', methods=['GET', 'POST'])
@login_required
def admin():
	if request.method == 'POST':
		action = request.form.get('action')
		if action == 'notes':
			return jsonify(result=model.set_admin_notes(request.form.get('notes')))
		else:
			return "Unrecognized Action"
	return show_admin(AdminPages.admin)

@app.route('/admin/login/', methods=['GET', 'POST'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('admin'))
	elif request.method == 'POST':
		email = request.form.get('email')
		if email:
			return jsonify(result=model.login_action_sendcode(email))
	else:
		email = request.args.get('email')
		code = request.args.get('code')
		if email and code:
			check = model.login_action_ceckcode(email, code)
			if check == 'success':
				login_user(model.login_get_user_by_email(email))
				return redirect(url_for('admin'))
			else:
				flash(check, 'danger')
	return render_page_standard(create_page_fromfile('Login', 'admin/login.html'))

@app.route('/admin/logout/')
@login_required
def logout():
	logout_user()
	flash("You have been logged out", "success")
	return redirect(url_for('main'))

@app.route('/admin/setup/', methods=['GET', 'POST'])
@login_required
def setup():
	if request.method == 'POST':
		#reset
		if(request.values.getlist('reset')):
			model.reset_db()
			flash("Database has been reset, all is lost", "danger")
		#website
		name = request.form['name']
		header = request.form['header']
		lang = request.form['language']
		model.set_site_info(name, header, lang)
		flash("Settings updated", "success")
		#default menu
		if(request.values.getlist('default')):
			model.create_default_menu()
			flash("Now showing a default menu", "warning")
		else:
			#menu
			titles = request.values.getlist('menu_title')
			targets = request.values.getlist('menu_target')
			menu = []
			curr = 0
			if model.set_menu(titles, targets):
				flash("Menu updated", "success")
		users = request.values.getlist('user')
		if len(users) == 0 or not model.set_user_list(users):
			flash("The site must have at least one active administrator", "danger")
		#testdata
		if(request.values.getlist('test')):
			model.create_test_data()
			flash("Data for testing has been created", "warning")
	return show_admin(AdminPages.setup)

@app.route('/admin/pages/', methods=['GET', 'POST'])
@login_required
def pages_admin():
	return show_admin(AdminPages.pages)

@app.route('/admin/pages/edit/', methods=['GET', 'POST'])
@login_required
def pages_edit():
	if request.method == 'POST':
		action = request.form.get('action')
		if action is None:
			model.page_action_edit(request.args.get('page'), request.form)
		else:
			page = request.form.get('page')
			if(action == 'delete'):
				return jsonify(result=model.page_action_delete(page))
			if(action == 'move'):
				return jsonify(result=model.page_action_move(page, request.form.get('target')))
			if(action == 'copy'):
				return jsonify(result=model.page_action_copy(page, request.form.get('target')))
			return jsonify(result='action not found')
	page = request.args.get('page')
	return render_page(create_page_fromfile('Edit Page \''+page+'\'', 'admin/pages/edit.html', **model.page_get_admin(page)), create_sidebar_fromfile('admin/pages/editbar.html'))

@app.route('/admin/pages/create/', methods=['GET', 'POST'])
@login_required
def pages_create():
	if request.method == 'POST':
		action = request.form.get('action')
		if action == 'check':
			return jsonify(result=model.page_action_check(request.form.get('path')))
	return show_admin(AdminPages.createpage)


@app.route('/admin/projects/', methods=['GET', 'POST'])
@login_required
def projects_admin():
	return show_admin(AdminPages.projects)

@app.route('/admin/projects/edit/', methods=['GET', 'POST'])
@login_required
def projects_edit():
	path = request.form.get('project')
	if request.method == 'POST':
		action = request.form.get('action')
		if action == 'move':
			return jsonify(result=model.project_move(path, request.form.get('target')))
		elif action == 'delete':
			return jsonify(result=model.project_delete(path))
	if not path or path == '':
		return show_admin(AdminPages.createproject)
	flash("Project editing not yet implemented", "warning")
	return render_page(create_page_fromfile('Edit Project', 'admin/projects/edit.html'))
	
@app.route('/admin/projects/create/', methods=['GET'])
@login_required
def projects_create():
	return show_admin(AdminPages.createproject)


@app.route('/admin/files/', methods=['GET', 'POST'])
@login_required
def files(embedded=False):
	path = request.args.get('path')
	filter = request.args.get('filter')
	if request.method == 'POST':
		files = request.files.getlist("files")
		if not path:
			path = "files"
		if files:
			for file in files:
				if not model.files_save_file(path, file):
					flash('Could not save %r' %file.name, 'danger')
			flash('Files saved', 'success')
		else:
			folder = request.form.get('folder')
			if folder:
				newpath = model.files_create_folder(path, folder)
				if newpath:
					flash('Folder created', 'success')
					if embedded:
						if filter:
							return redirect(url_for('files_embed', path=newpath, filter=filter))
						else:
							return redirect(url_for('files_embed', path=newpath))
					else:
						if filter:
							return redirect(url_for('files', path=newpath, filter=filter))
						else:
							return redirect(url_for('files', path=newpath))
				else:
					flash('Invalid folder name', 'danger')
			else:
				flash('Faulty Request', 'danger')
	if path:
		if embedded:
			return render_page_embed_fromfile('', 'admin/files.html', **model.files_list(path, filter))
		else:
			return create_page_admin('Folder: %r' %path, 'admin/files.html', **model.files_list(path, filter))
	else:
		if embedded:
			return render_page_embed_fromfile('', 'admin/files.html', **model.files_list(filter=filter))
		else:
			return create_page_admin('Files', 'admin/files.html', **model.files_list(filter=filter))

@app.route('/admin/files/embed/', methods=['GET', 'POST'])
@login_required
def files_embed():
	return files(True)


@app.route('/admin/messages/', methods=['GET', 'POST'])
@login_required
def messages():
	if request.method == 'POST':
		try:
			action = request.form['action']
			if action == 'read':
				return jsonify(result=model.message_action_read(request.form['message']))
			if action == 'unread':
				return jsonify(result=model.message_action_unread(request.form['message']))
			elif action == 'delete':
				return jsonify(result=model.message_action_delete(request.form['message']))
			elif action == 'send':
				return jsonify(result=model.message_action_send(request.form.get('message')))
		except KeyError as e:
			return jsonify(result=e.message)
	else:
		return show_admin(AdminPages.messages)

@app.route('/admin/messages/blacklist/', methods=['GET', 'POST'])
@login_required
def blacklist():
	if request.method == 'POST':
		try:
			action = request.form['action']
			if action == 'ban':
				return jsonify(result=model.message_action_ban(request.form['phrase']))
			elif action == 'unban':
				return jsonify(result=model.message_action_unban(request.form['phrase']))
			elif action == 'checkall':
				return jsonify(result=model.message_action_recheck_all())
		except KeyError as e:
			return jsonify(result=e.message)
		return jsonify(result='Action not recognized')
	else:
		return show_admin(AdminPages.blacklist)

@app.route('/admin/messages/forwarding/', methods=['GET', 'POST'])
@login_required
def forwarding():
	if request.method == 'POST':
		action = request.form.get('action')
		if action:
			if action == 'remove':
				return jsonify(result=model.message_forward_remove(request.form.get('email')))
		else:
			email = request.form.get('email')
			type = request.form.get('type')
			if email and type:
				model.message_forward_add(email, type)
	return show_admin(AdminPages.forwarding)

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

@app.route('/admin/edit/', methods=['GET'])
@login_required
def edit_item():
	path = request.args.get('path')
	if path:
		if path == '/':
			return redirect(url_for('pages_edit', page=path), 303)
		if '/pages/' == path:
			return redirect(url_for('pages_admin'), 303)
		if '/pages/' in path:
			return redirect(url_for('pages_edit', page=path.replace('/pages/', '')), 303)
		if path == '/contact/':
			return redirect(url_for('messages'), 303)
		if '/projects/' == path:
			return redirect(url_for('projects_admin'), 303)
		if '/projects/' in path:
			return redirect(url_for('projects_edit', page=path.replace('/projects/', '')), 303)
	flash('Path not recognized', 'error')
	return redirect(url_for('admin'), 303)


### pages ###
@app.route('/pages/')
def pages():
	return render_page_standard(create_page_fromfile("Pages", 'frontend/pages.html', pages=model.page_list()), True)

@app.route('/pages/<path:page>/')
def page(page):
	return show_page(page)

### projects ###
@app.route('/projects/')
def projects():
	tags =  request.args.getlist('tag')
	order = request.args.get('sorting')
	title = "Projects"
	if len(tags) > 0:
		if len(tags) == 1:
			title += " (Tag: %s)" %tags[0]
		else:
			title += " (Tags: %s)" %', '.join(tags)
	return render_page(create_page_fromfile(title, 'frontend/projects/projects.html', projects=model.project_list(tags, order)),\
	    create_sidebar_fromfile("frontend/projects/sidebar.html", tags=model.project_tags()), True)

@app.route('/projects/<path:project>/')
def project(project):
	return show_project(project)

### contact ###
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
							return render_page_standard(create_page_fromfile('Contact', 'frontend/contact.html'), True)
						else:
							flash('ReCaptcha not valid', 'error')
			return render_page_standard(create_page_fromfile('Contact', 'frontend/contact.html', email=email, subject=subject, message=message, check=True), True)
	return render_page_standard(create_page_fromfile('Contact', 'frontend/contact.html'), True)


### files ###
@app.route('/files/<path:filename>')
def uploaded_file(filename):
    return send_from_directory('files/', filename)


### errors ###
@app.errorhandler(404)
def page_not_found(error):
	flash("Page not found, returning to main", "danger")
	return redirect(url_for('main'), 303)

@app.errorhandler(403)
@app.errorhandler(401)
@login_manager.unauthorized_handler
def not_logged_in():
	flash('<a href="'+url_for('login')+'">Access Denied</a>', "warning")
	return redirect(url_for('main'), 303)
