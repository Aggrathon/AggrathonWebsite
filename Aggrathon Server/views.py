from flask import Flask
from app import app
from page import *
import sys

#ROUTES

@app.route('/')
def main():
	return render_page_standard({'html':"This is the mainpage"})

@app.route('/projects/')
def projects():
    return show_page_html_sidebar_html("Projects", "This is the projects page", "Here is a custom sidebar")

@app.route('/stuff/')
def stuff():
	return show_page_html("Stuff", "stuff stuff stuff stuff stuff stuff stuff stuff stuff")

@app.route('/pages/<page>/')
def page(page):
    return show_page_html(page, "Page: "+page)

@app.route('/projects/<project>/')
def project(project):
    return show_page_html(project, "Custom Project: "+project)

@app.route('/<path:url>/')
def catcher(url):
    return render_page_standard({'html':"This is the main page", 'alert':'Page not found, returning to main'})