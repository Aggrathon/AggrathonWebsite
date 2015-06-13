from flask import Flask
from app import app
from page import *
import database

#ROUTES

@app.route('/')
def main():
	return render_page_standard({'html':"This is the mainpage"})

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

@app.route('/<path:url>/')
def catcher(url):
	return render_page_standard({'html':"This is the main page", 'alert':'Page not found, returning to main'})