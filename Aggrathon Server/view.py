"""
	File containing all methods required for rendering pages
"""
from flask import render_template, flash, abort, request
from flask_login import current_user
from app import app
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
def render_page(pageInfo, sidebarInfo=None, editable=False):
	return __render_page(model.get_site_info(editable), pageInfo, sidebarInfo)

# renders the page with the standard siteInfo and sidebar
def render_page_standard(pageInfo, editable=False):
	return render_page(pageInfo, create_sidebar_featured(), editable)

"""
	Methods for rendering embedded pages (without header)
"""
def __render_page_embed(siteInfo, pageInfo, sidebarInfo=None):
	return render_template("layout/embed.html", site=siteInfo, content=pageInfo)

def render_page_embed(pageInfo):
	return __render_page_embed(model.get_site_info_embed(), pageInfo)

def render_page_embed_sidebar(pageInfo, sidebarInfo=None):
	return __render_page_embed(model.get_site_info_embed(), pageInfo, sidebarInfo)

def render_page_embed_fromfile(title, file, **data):
	return render_page_embed( {'title':title, 'file':file, 'data':data} )

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
	return create_sidebar_fromfile("admin/sidebar.html")


"""
	Methods for rendering pages of standard types
"""
def show_page(path):
	page = model.page_get(path)
	return render_page_standard(create_page(page.title, page.content), True)


"""
	Methods for rendering projects of standard types
"""
def show_project(path):
	project = model.project_get(path)
	return render_page_standard(create_page_fromfile(file='frontend/projects/project.html', **project), True)


"""
	Admin pages
"""
from enum import Enum
class AdminPages(Enum):
	admin = 1
	setup = 2
	pages = 3
	createpage = 8
	projects = 4
	messages = 6
	blacklist = 7
	forwarding = 9

def show_admin(page):
	if page is AdminPages.admin:
		return create_page_admin('Admin', 'admin/overview.html', **model.get_admin_front())
	if page is AdminPages.setup:
		return create_page_admin('Setup', 'admin/setup.html', users=model.get_user_list(), **model.get_site_info())
	if page is AdminPages.pages:
		return create_page_admin('Pages', 'admin/pages/pages.html', pages=model.page_list_admin())
	if page is AdminPages.createpage:
		return create_page_admin('Create Page', 'admin/pages/create.html')
	if page is AdminPages.projects:
		return create_page_admin('Projects', 'admin/projects/projects.html')
	if page is AdminPages.messages:
		return create_page_admin('Messages', 'admin/messages/messages.html', **model.message_list(try_int(request.args.get("start"), 1) - 1, try_int(request.args.get("amount"), 20)))
	if page is AdminPages.blacklist:
		return create_page_admin("Message Blacklist", 'admin/messages/blacklist.html', blacklist=model.message_blacklist())
	if page is AdminPages.forwarding:
		return create_page_admin("Message Forwarding", 'admin/messages/forwarding.html', forwardlist=model.message_forward_list())
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

