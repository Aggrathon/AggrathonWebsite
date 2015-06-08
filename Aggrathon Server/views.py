from flask import Flask
from app import app
from page import show_page, render_page

#ROUTES

@app.route('/')
def main():
    return render_page(html="This is the mainpage")

@app.route('/projects/')
def projects():
    return show_page("Projects", None, "This is the projects page", None, "Here is a custom sidebar", None, False)

@app.route('/stuff/')
def stuff():
    return render_page(title="Stuff", html="stuff stuff stuff stuff stuff stuff stuff stuff stuff")

@app.route('/pages/<page>/')
def page(page):
    return render_page(title=page, html="Page: "+page)

@app.route('/projects/<project>/')
def project(project):
    return render_page(title=project, html="Custom Project: "+project)

@app.route('/<path:url>/')
def catcher(url):
    return render_page(html="This is the main page", alert='Page not found, returning to main')