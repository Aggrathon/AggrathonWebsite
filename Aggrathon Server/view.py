﻿"""
	File containing all methods required for rendering pages
"""
from flask import render_template, flash, abort, request
import model

"""
	Main method for rendering pages

	arguments:

	siteInfo = {name, header, language, menu}
		name: shown in the title
		header: the big text in the title
		language: language-code eg. "en"
		menu: list of menu-items = {title, target}
			target: target of the link
			title: text to show on the button
	pageInfo = {title, html, file, data}
		title: the header of the page (also shown in the title)
		html: the content of the page as a string (may contain html)
		file: url to a file containing the content of the page (can be jinja2)
		data: the data to send to the contentfile	
	sidebarInfo = {html, file, data}: if this object is present the sidebar is shown (otherwise no sidebar)
		html: text/html that is a custom sidebar
		file: url to a file containing a custom sidebar
		data: the data to send to the sidebarfile
"""
def __render_page(siteInfo, pageInfo, sidebarInfo=None):
	return render_template("layout/layout.html", site=siteInfo, content=pageInfo, sidebar=sidebarInfo)

# renders the page with the standard siteInfo
def render_page(pageInfo, sidebarInfo=None):
	return __render_page(model.get_site_info(), pageInfo, sidebarInfo)

# renders the page with the standard siteInfo and sidebar
def render_page_standard(pageInfo):
	return render_page(pageInfo, create_sidebar_featured())


"""
	Methods for creating custom pages and sidebars inline
"""
def create_page(title, html):
	return {'title':title, 'html':html}

def create_sidebar(sidebar):
	return {'html':sidebar}


"""
	Methods for creating custom pages and sidebars from files
"""
def create_page_fromfile(title, file, **data):
	return {'title':title, 'file':file, 'data':data}

def create_sidebar_fromfile(file, **data):
	return {'file':file, 'data':data}


"""
	Standard sidebars
"""
def create_sidebar_featured():
	pages = model.featured_pages()
	projects = model.featured_projects()
	if(pages is None and projects is None):
		return None
	else:
		return create_sidebar_fromfile("frontend/sidebar_featured.html", featuredPages=pages, featuredProjects=projects)

def create_sidebar_admin():
	return create_sidebar_fromfile("admin/sidebar.html", unread_messages=model.message_unread_count())


"""
	Methods for rendering pages of standard types
"""
def show_page(path):
	page = model.page_get(path)
	return render_page_standard(create_page(page.title, page.content))


"""
	Admin pages
"""
from enum import Enum
class AdminPages(Enum):
	admin = 1
	setup = 2
	pages = 3
	projects = 4
	files = 5
	messages = 6
	blacklist = 7

def show_admin(page):
	#if not isloggedin:
		#abort(403)
	if page is AdminPages.admin:
		return create_page_admin('Admin', 'admin/overview.html', **model.get_stats())
	if page is AdminPages.setup:
		return create_page_admin('Setup', 'admin/setup.html', **model.get_site_info())
	if page is AdminPages.pages:
		return create_page_admin('Pages', 'admin/pages/pages.html', pages=model.page_list())
	if page is AdminPages.projects:
		return create_page_admin('Projects', 'admin/projects/projects.html')
	if page is AdminPages.files:
		return create_page_admin('Files', 'admin/files.html')
	if page is AdminPages.messages:
		return create_page_admin('Messages', 'admin/messages/messages.html', **model.message_list(try_int(request.args.get("start"), 1) - 1, try_int(request.args.get("amount"), 20)))
	if page is AdminPages.blacklist:
		return create_page_admin("Message Blacklist", 'admin/messages/blacklist.html', blacklist=model.message_blacklist())
	else:
		flash("Unrecognized call for adminpage, showing main adminpage", "warning")
		return show_admin(AdminPages.admin)

def create_page_admin(title, file, **kwargs):
	return render_page(create_page_fromfile(title, file, **kwargs), create_sidebar_admin())

def try_int(value, default):
	try:
		return int(value)
	except (ValueError, TypeError):
		return default

def show_project(project):
	return render_page(create_page_fromfile(project, 'frontend/projects/project.html'))
