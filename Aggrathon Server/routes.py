from flask import Flask, request, flash, redirect, url_for, jsonify
from app import app
from view import *
import model

### ROUTES ###

### main ###
@app.route('/')
def main():
	return show_page('/')

### admin ###
@app.route('/admin/')
def admin():
	if not model.check_if_setup():
		try:
			model.create_db()
			flash("Website initialized successfully", "success")
		except:
			flash("Unable to setup database, check config or use the 'Reset Database' function to remove old data", "danger")
		return redirect(url_for('setup'))
	return show_admin(AdminPages.admin)

@app.route('/login/')
def login():
	return render_page_standard(create_page_fromfile('Login', 'admin/login.html'))

@app.route('/admin/setup/', methods=['GET', 'POST'])
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
		model.setup(name, header, lang)
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
def pages_admin():
	return show_admin(AdminPages.pages)

@app.route('/admin/pages/edit/', methods=['GET', 'POST'])
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
def pages_create():
	if request.method == 'POST':
		action = request.form.get('action')
		if action == 'check':
			return jsonify(result=model.page_action_check(request.form.get('path')))
	return show_admin(AdminPages.createpage)

@app.route('/admin/projects/', methods=['GET', 'POST'])
def projects_admin():
	return show_admin(AdminPages.projects)

@app.route('/admin/files/', methods=['GET', 'POST'])
def files():
	path = request.args.get('path')
	if path:
		return create_page_admin('Files: %r' %path, 'admin/files.html', **model.files_list(path))
	else: 
		return create_page_admin('Files', 'admin/files.html', **model.files_list())

@app.route('/admin/messages/', methods=['GET', 'POST'])
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
		except KeyError as e:
			return jsonify(result=e.message)
	else:
		return show_admin(AdminPages.messages)

@app.route('/admin/messages/blacklist/', methods=['GET', 'POST'])
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


### errors ###
@app.errorhandler(404)
def page_not_found(error):
	flash("Page not found, returning to main", "danger")
	return redirect(url_for('main'), 303)

@app.errorhandler(403)
def not_logged_in(error):
	flash("Access Denied", "danger")
	return redirect(url_for('login'), 303)