from flask import Flask, request, flash, redirect, url_for
from app import app
from page import *
import database

### ROUTES ###

### main ###
@app.route('/')
def main():
	return show_page('/')

### admin ###
@app.route('/admin/')
def admin():
	if not database.check_if_setup():
		try:
			database.create_db()
			flash("Website initialized successfully", "success")
		except:
			flash("Unable to setup database, check config or use the 'Reset Database' function to remove old data", "danger")
		return redirect(url_for('setup'))
	return render_page(create_custom_page("Admin", "admin/overview.html", **database.getStats()), create_custom_sidebar("admin/sidebar.html"))

@app.route('/admin/setup/', methods=['GET', 'POST'])
def setup():
	if request.method == 'POST':
		#reset
		if(request.values.getlist('reset')):
			database.reset_db()
			flash("Database has been reset, all is lost", "danger")
		#testdata
		if(request.values.getlist('test')):
			database.createTestData()
			flash("Data for testing has been created", "warning")
		else:
			#website
			name = request.form['name']
			header = request.form['header']
			lang = request.form['language']
			database.setup(name, header, lang)
			#menu
			titles = request.values.getlist('menu_title')
			targets = request.values.getlist('menu_target')
			menu = []
			curr = 0
			while curr < len(titles):
				menu.append({'title': titles[curr], 'target':targets[curr]})
				curr += 1
			database.setMenu(menu)
			flash("Settings updated", "success")
	site = database.getSiteInfo()
	return render_page(create_custom_page("Setup", "admin/setup.html", **site), create_custom_sidebar("admin/sidebar.html"))

@app.route('/admin/pages/', methods=['GET', 'POST'])
def pages_admin():
	flash("Not implemented", "danger")
	return redirect(url_for('admin'), 303)

@app.route('/admin/projects/', methods=['GET', 'POST'])
def projects_admin():
	flash("Not implemented", "danger")
	return redirect(url_for('admin'), 303)

@app.route('/admin/files/', methods=['GET', 'POST'])
def files():
	flash("Not implemented", "danger")
	return redirect(url_for('admin'), 303)

@app.route('/admin/messages/', methods=['GET', 'POST'])
def messages():
	flash("Not implemented", "danger")
	return redirect(url_for('admin'), 303)

### pages ###
@app.route('/pages/<path:path>/edit/')
def page_edit(path):
	path = "/pages/"+path+"/"
	flash("Page editing not yet implemented", "warning")
	return show_page(path)

@app.route('/pages/<path:path>/')
def page(path):
	flash("Not implemented", "danger")
	return show_page("/pages/"+path+"/")

@app.route('/pages/')
def pages(path):
	flash("Not implemented", "danger")
	return create_page("Pages", "Here is a list of all the pages")

### projects ###
@app.route('/projects/<path:path>/edit/')
def page_edit(path):
	path = "/projects/"+path+"/"
	flash("Project editing not yet implemented", "warning")
	return show_page(path)

@app.route('/projects/')
def projects():
	flash("Not implemented", "danger")
	return create_page_sidebar("Projects", "This is the projects page", "Here is a custom sidebar")

@app.route('/projects/<project>/')
def project(project):
	flash("Projects not fully implemented", "warning")
	return create_page(project, "Custom Project: "+project)

### contact ###
@app.route('/contact/', methods=['GET', 'POST'])
def contact():
	flash("Not implemented", "danger")
	return create_page("Contact", "[Insert contact form]")


### misc ###

### errors ###
@app.errorhandler(404)
def page_not_found(error):
	flash("Page not found, returning to main", "danger")
	return redirect(url_for('main'), 303)