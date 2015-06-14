from flask import Flask, request, flash, redirect, url_for
from app import app
from page import *
import database

#ROUTES

#main
@app.route('/')
def main():
	return render_page_standard({'html':"This is the mainpage<br /><a href='admin/setup/'>Setup</a>"})

#admin
@app.route('/admin/')
def admin():
	if not database.check_if_setup():
		try:
			database.create_db()
			flash("Website initialized successfully", "success")
		except:
			flash("Unable to setup database, check config or use the 'Reset Database' function to remove old data", "danger")
		return redirect(url_for('setup'))
	return show_page_sidebar("Admin", "Important data here", '<h3>Admin</h3><a href="setup/">Setup</a><br />other links')

@app.route('/admin/setup/', methods=['GET', 'POST'])
def setup():
	if request.method == 'POST':
		#reset
		if(request.values.getlist('reset')):#.form['reset']):
			database.reset_db()
			flash("Database has been reset, all is lost", "danger")
		#testdata
		if(request.values.getlist('test')):#form['test']):
			database.createTestData()
			flash("Data for testing has been created", "warning")
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
	return render_page(create_custom_page("Setup", "admin/setup.html", **site),None)


@app.route('/projects/')
def projects():
    return show_page_sidebar("Projects", "This is the projects page", "Here is a custom sidebar")

@app.route('/stuff/')
def stuff():
	return show_page("Stuff", "stuff stuff stuff stuff stuff stuff stuff stuff stuff")

@app.route('/pages/<path:path>/')
def page(path):
	path = "/pages/"+path+"/"
	print (path)
	page = database.getPage(path)
	return show_page(page.title, page.content)

@app.route('/projects/<project>/')
def project(project):
	return show_page(project, "Custom Project: "+project)

@app.errorhandler(404)
def page_not_found(error):
	flash("Page not found, returning to main", "danger")
	return redirect(url_for('main'), 303)