from flask import Flask, request, flash, redirect, url_for, jsonify, send_from_directory
from app import app, login_manager
from flask_login import login_user, logout_user, login_required, current_user
from view import *
import model

### ROUTES ###

### main ###
@app.route('/')
def main():
	return show_page('/')

### admin ###
@app.route('/admin/')
@login_required
def admin():
	if not model.check_if_setup():
		try:
			model.create_db()
			flash("Website initialized successfully", "success")
		except:
			flash("Unable to setup database, check config or use the 'Reset Database' function to remove old data", "danger")
		return redirect(url_for('setup'))
	return show_admin(AdminPages.admin)

@app.route('/admin/login/', methods=['GET', 'POST'])
def login():
	if current_user.is_authenticated():
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
			while curr < len(titles):
				menu.append({'title': titles[curr], 'target':targets[curr]})
				curr += 1
			model.set_menu(menu)
			flash("Menu updated", "success")
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

@app.route('/admin/files/', methods=['GET', 'POST'])
@login_required
def files(embedded=False):
	path = request.args.get('path')
	filter = request.args.get('filter')
	if request.method == 'POST':
		if path:
			files = request.files.getlist("files")
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
								return redirect(url_for('files_embed')+'?path='+newpath+'&filter='+filter)
							else:
								return redirect(url_for('files_embed')+'?path='+newpath)
						else:
							if filter:
								return redirect(url_for('files')+'?path='+newpath+'&filter='+filter)
							else:
								return redirect(url_for('files')+'?path='+newpath)
					else:
						flash('Invalid folder name', 'danger')
				else:
					flash('Faulty Request', 'danger')
		else:
			flash('Invalid Path', 'warning')
	if path:
		if embedded:
			return render_page_embed_fromfile('', 'admin/files.html', **model.files_list(path, filter))
		else:
			return create_page_admin('File: %r' %path, 'admin/files.html', **model.files_list(path, filter))
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

@app.route('/admin/projects/create/', methods=['GET', 'POST'])
@login_required
def edit_project(project=''):
	if project == '':
		flash("Project creation not implemented", "danger")
		return render_page(create_page_fromfile('Create Project', 'admin/projects/edit.html'))
	else:
		flash("Project editing not yet implemented", "warning")
		return render_page(create_page_fromfile('Edit Project', 'admin/projects/edit.html'))

### pages ###
@app.route('/pages/')
def pages():
	return render_page_standard(create_page_fromfile("Pages", 'frontend/pages.html', pages=model.page_list()))

@app.route('/pages/<path:path>/')
def page(path):
	return show_page(path)

### projects ###
@app.route('/projects/')
def projects():
	flash("Not implemented", "danger")
	return render_page(create_page_fromfile("Projects", 'frontend/projects/projects.html'), create_sidebar_fromfile("frontend/projects/sidebar.html"))

@app.route('/projects/<path:project>/')
def project(project):
	flash("Projects not fully implemented", "warning")
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
						model.message_add(email, subject, message)
						flash('Message sent', 'success')
						return render_page_standard(create_page_fromfile('Contact', 'frontend/contact.html'))
			return render_page_standard(create_page_fromfile('Contact', 'frontend/contact.html', email=email, subject=subject, message=message, check=True))
	return render_page_standard(create_page_fromfile('Contact', 'frontend/contact.html'))


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
