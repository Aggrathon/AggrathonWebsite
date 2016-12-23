"""
	File containing all methods required for rendering pages
"""
from flask import render_template, flash, abort, request, url_for
from flask_login import current_user
from app import app, get_hook, HOOK_SIDEBAR_FEATURED_LIST, HOOK_ADMIN_SIDEBAR
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
def create_page_fromfile(title, file, hide_title=False, **data):
	return {'title':title, 'file':file, 'hide_title':hide_title, 'data':data}

def create_sidebar_fromfile(file, **data):
	return {'file':file, 'data':data}


"""
	Standard sidebars
"""
def create_sidebar_featured():
	feats = []
	for list in get_hook(HOOK_SIDEBAR_FEATURED_LIST):
		result = list()
		if result:
			feats.append(result)
	if(len(feats) == 0):
		return None
	else:
		return create_sidebar_fromfile("frontend/sidebar_featured.html", featured=feats)

def create_sidebar_admin():
	links = [
		(url_for('admin'), 'Overview', [], ''), 
		(url_for('setup'), 'Setup', [], ''), 
		(url_for('pages_admin'), 'Pages', [(url_for('pages_create'), 'Create Page')], '')
		]
	for link in get_hook(HOOK_ADMIN_SIDEBAR):
		links.append(link())
	links.append((url_for('files'), 'Files', [], ''))
	links.append((url_for('logout'), 'Log Out', [], ''))
	return create_sidebar_fromfile("admin/sidebar.html", links=links)


"""
	Methods for rendering pages of standard types
"""
def show_page(path):
	page = model.page_get(path)
	return render_page_standard(create_page(page.title, page.content), True)


"""
	Admin pages
"""
def create_page_admin(title, file, **kwargs):
	return render_page(create_page_fromfile(title, file, **kwargs), create_sidebar_admin())


"""
	Utils
"""

def try_int(value, default):
	try:
		return int(value)
	except (ValueError, TypeError):
		return default

@app.template_filter('datetime')
def _jinja2_filter_datetime(date):
    return date.strftime('%Y-%m-%d') 
