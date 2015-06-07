from flask import Flask
from app import *

@app.route('/')
def main():
    return show_page("", "This is the mainpage", "", True)

@app.route('/projects/')
def projects():
    return show_page("Projects", "This is the projects page", "", False)

@app.route('/stuff/')
def stuff():
    return show_page("Projects", "stuff stuff", "", True)