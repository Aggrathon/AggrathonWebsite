"""
	File containing all methods required for rendering pages
"""
from flask import render_template
import database


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
def create_custom_page(title, file, **data):
	return {'title':title, 'file':file, 'data':data}

def create_custom_sidebar(file, **data):
	return {'file':"featured.html", 'data':data}



"""
	Methods for getting the standard siteInfo and sidebar
"""
def __getSiteInfo():
	return database.getSiteInfo()

def create_featured_sidebar():
	pages = __featured_sidebar_pages()
	projects = __featured_sidebar_projects()
	if(pages is None and projects is None):
		return None
	else:
		return create_custom_sidebar("featured.html", featuredPages=pages, featuredProjects=projects)

def __featured_sidebar_pages():
	return database.getFeaturedPages()

def __featured_sidebar_projects():
	return database.getFeaturedProjects()
	#return [{'img':"/static/background.jpg", 'url':"/projects/test", 'title':'poject1', 'description':'hjdfkas afhfsadjfasd asdfjhfdaskhka'},\
	#   {'img':"", 'url':"/projects/", 'title':'asd assad jkd as sdajahsd kjdh', 'description':'hjdfkas afhf sadj fasd asdfjhfd askhka klas a asdklj daskas kdjsad jasöljd skaljas kjdkasj das djkljd klas djas'}]



"""
	Simple Methods for rendering pages
"""
#Pages with standard sidebar
def show_page(title, html):
	return render_page_standard({'title':title, 'html':html})

#Pages with no sidebar
def show_page_nosidebar(title, html):
	return render_page({'title':title, 'html':html}, None)

#Pages with sidebar
def show_page_sidebar(title, html, sidebar):
	return render_page({'title':title, 'html':html}, {'html':sidebar})
