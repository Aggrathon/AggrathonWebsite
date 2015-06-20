from flask import Flask, request, flash, redirect, url_for
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
			model.createDefaultMenu()
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
			model.setMenu(menu)
			flash("Menu updated", "success")
		#testdata
		if(request.values.getlist('test')):
			model.createTestData()
			flash("Data for testing has been created", "warning")
	return show_admin(AdminPages.setup)

@app.route('/admin/pages/', methods=['GET', 'POST'])
def pages_admin():
	return show_admin(AdminPages.pages)

@app.route('/admin/projects/', methods=['GET', 'POST'])
def projects_admin():
	return show_admin(AdminPages.projects)

@app.route('/admin/files/', methods=['GET', 'POST'])
def files():
	return show_admin(AdminPages.files)

@app.route('/admin/messages/', methods=['GET', 'POST'])
def messages():
	return show_admin(AdminPages.messages)

@app.route('/admin/pages/create/', methods=['GET', 'POST'])
def edit_page(path=''):
	if path == '':
		flash("Page creation not implemented", "danger")
		return render_page(create_page_fromfile('Create Page', 'pages/edit.html'))
	else:
		flash("Page editing not yet implemented", "warning")
		return render_page(create_page_fromfile('Edit Page', 'pages/edit.html'))

@app.route('/admin/projects/create/', methods=['GET', 'POST'])
def edit_project(project=''):
	if project == '':
		flash("Project creation not implemented", "danger")
		return render_page(create_page_fromfile('Create Project', 'projects/edit.html'))
	else:
		flash("Project editing not yet implemented", "warning")
		return render_page(create_page_fromfile('Edit Project', 'projects/edit.html'))

### pages ###
@app.route('/pages/')
def pages():
	flash("Not implemented", "danger")
	return render_page(create_page_fromfile("Pages", 'pages/pages.html'))

@app.route('/pages/<path:path>/edit/')
def page_edit(path):
	return edit_page("/pages/"+path+"/")

@app.route('/pages/<path:path>/')
def page(path):
	flash("Not implemented", "danger")
	return show_page("/pages/"+path+"/")

### projects ###
@app.route('/projects/')
def projects():
	flash("Not implemented", "danger")
	return render_page(create_page_fromfile("Projects", 'projects/projects.html'), create_sidebar_fromfile("projects/sidebar.html"))

@app.route('/projects/<path:project>/edit/')
def project_edit(project):
	flash("Project editing not yet implemented", "warning")
	return edit_project(project)

@app.route('/projects/<path:project>/')
def project(project):
	flash("Projects not fully implemented", "warning")
	return show_project(project)

### contact ###
@app.route('/contact/', methods=['GET', 'POST'])
def contact():
	flash("Not implemented", "danger")
	return create_page("Contact", "[Insert contact form]")


### misc ###
@app.route('/edit/', methods=['GET', 'POST'])
def main_edit():
	return edit_page('/')

### errors ###
@app.errorhandler(404)
def page_not_found(error):
	flash("Page not found, returning to main", "danger")
	return redirect(url_for('main'), 303)

@app.errorhandler(403)
def not_logged_in(error):
	flash("You are not logged in!", "danger")
	return redirect(url_for('login'), 303)