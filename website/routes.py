from flask import Flask, request, flash, redirect, url_for, send_from_directory, jsonify, get_flashed_messages
from app import app, login_manager, recaptcha, HOOK_EDIT_CONTENT, get_hook
from flask_login import login_user, logout_user, login_required, current_user
from view import *
import model

### ROUTES ###

### main ###
@app.route('/')
def main():
	return show_page('/')

#region admin
@app.route('/admin/', methods=['GET'])
@login_required
def admin():
	return create_page_admin('Admin', 'admin/overview.html', hide_title=True, widgets=model.get_admin_widgets())

@app.route('/admin/login/', methods=['GET', 'POST'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('admin'))
	elif request.method == 'POST':
		email = request.form.get('email')
		if email:
			return model.login_action_sendcode(email)
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
	return create_page_admin('Setup', 'admin/setup.html', users=model.get_user_list(), **model.get_site_info())

@app.route('/admin/pages/', methods=['GET', 'POST'])
@login_required
def pages_admin():
	return create_page_admin('Pages', 'admin/pages/pages.html', pages=model.page_list_admin())

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
				return model.page_action_delete(page)
			if(action == 'move'):
				return model.page_action_move(page, request.form.get('target'))
			if(action == 'copy'):
				return model.page_action_copy(page, request.form.get('target'))
			return 'action not found'
	page = request.args.get('page')
	return render_page(create_page_fromfile('Edit Page \''+page+'\'', 'admin/pages/edit.html', **model.page_get_admin(page)), create_sidebar_fromfile('admin/pages/editbar.html'))

@app.route('/admin/pages/create/', methods=['GET', 'POST'])
@login_required
def pages_create():
	if request.method == 'POST':
		action = request.form.get('action')
		if action == 'check':
			return model.page_action_check(request.form.get('path'))
	return create_page_admin('Create Page', 'admin/pages/create.html')


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
			return create_page_admin('Files', 'admin/files.html', **model.files_list(path, filter))
	else:
		if embedded:
			return render_page_embed_fromfile('', 'admin/files.html', **model.files_list(filter=filter))
		else:
			return create_page_admin('Files', 'admin/files.html', **model.files_list(filter=filter))

@app.route('/admin/files/embed/', methods=['GET', 'POST'])
@login_required
def files_embed():
	return files(True)

@app.route('/admin/edit/', methods=['GET'])
@login_required
def edit_item():
	path = request.args.get('path')
	if path:
		for hook in get_hook(HOOK_EDIT_CONTENT):
			ret = hook(path)
			if ret is not None:
				return ret
	flash('Path not recognized', 'error')
	return redirect(url_for('admin'), 303)

#endregion

### pages ###
@app.route('/pages/')
def pages():
	return render_page_standard(create_page_fromfile("Pages", 'frontend/pages.html', pages=model.page_list()), True)

@app.route('/pages/<path:page>/')
def page(page):
	return show_page(page)

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
