﻿"""
	File containing all methods required for rendering pages
"""
from flask import render_template


"""
	Main method for rendering pages

	arguments:

	siteInfo = {name, header, menu}
		name: shown in the title
		header: the big text in the title
		menu: list of menu-items = {url, title}
			url: target of the link
			title: text to show on the button
			data: the data to send to the sidebarfile
	pageInfo = {title, alert, html, file, data}
		title: the header of the page (also shown in the title)
		alert: html/text to be shown in an dismissable alert box above the main content
		html: the content of the page as a string (may contain html)
		file: url to a file containing the content of the page (can be jinja2)
		data: the data to send to the contentfile	
	sidebarInfo = {html, file, data}: if this object is present the sidebar is shown (otherwise no sidebar)
		html: text/html that is a custom sidebar
		file: url to a file containing a custom sidebar
		data: the data to send to the sidebarfile
"""
def __render_page(siteInfo, pageInfo, sidebarInfo=None):
	return render_template("page.html", site=siteInfo, content=pageInfo, sidebar=sidebarInfo)

# renders the page with the standard siteInfo
def render_page(pageInfo, sidebarInfo=None):
	return __render_page(__getSiteInfo(), pageInfo, sidebarInfo)

# renders the page with the standard siteInfo and sidebar
def render_page_standard(pageInfo):
	return render_page(pageInfo, create_featured_sidebar())



"""
	Methods for creating custom pages and sidebars
"""
def create_custom_page(title, file, alert=None, **data):
	return {'title':title, 'file':file, 'alert':alert, 'data':data}

def create_custom_sidebar(file, **data):
	return {'file':"featured.html", 'data':data}



"""
	Methods for getting the standard siteInfo and sidebar
"""
def __getSiteInfo():
	#Create the standard site info
	return {'name':"Aggrathon", 'header':"Aggrathon.com", 'menu':[{'url':"/", 'title':"Home"},{'url':"/stuff/", 'title':"Stuff"},{'url':"/about/", 'title':"About"},{'url':"/projects/", 'title':"Projects"}]}

def create_featured_sidebar():
	pages = __featured_sidebar_pages()
	projects = __featured_sidebar_projects()
	if(pages is None and projects is None):
		return None
	else:
		return create_custom_sidebar("featured.html", featuredPages=pages, featuredProjects=projects)

def __featured_sidebar_pages():
    #Create featured sidebar
	#return None
    return [{'url':"/pages/test/", 'title':'page1', 'description':'hjdfkas afhfsadjfasd asdfjhfdaskhka'}, {'img':"", 'url':"/stuff/", 'title':'page2', 'description':'hjdfkas afhf sadj fasd asdfjhfd askhka'}]
def __featured_sidebar_projects():
    #Create featured sidebar
	#return None
	return [{'img':"/static/background.jpg", 'url':"/projects/test", 'title':'poject1', 'description':'hjdfkas afhfsadjfasd asdfjhfdaskhka'}, {'img':"", 'url':"/projects/", 'title':'asd assad jkd as sdajahsd kjdh', 'description':'hjdfkas afhf sadj fasd asdfjhfd askhka klas a asdklj daskas kdjsad jasöljd skaljas kjdkasj das djkljd klas djas'}]



"""
	Simple Methods for rendering pages
"""
#Pages with standard sidebar
def show_page(title, html, alert=None):
	return render_page_standard({'title':title, 'alert':alert, 'html':html})

#Pages with no sidebar
def show_page_nosidebar(title, html, alert=None):
	return render_page({'title':title, 'alert':alert, 'html':html}, None)

#Pages with sidebar
def show_page_sidebar(title, html, sidebar, alert=None):
	return render_page({'title':title, 'alert':alert, 'html':html}, {'html':sidebar})
