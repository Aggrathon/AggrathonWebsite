"""
	File containing all methods required for rendering pages
"""
from flask import render_template


"""
	Main methods for rendering pages

	arguments:
		siteInfo = {name, header, menu}
			name: shown in the title
			header: the big text in the title
			menu: list of menu-items = {url, title}
				url: target of the link
				title: text to show on the button
		content = {title, alert, html, page}
			title: the header of the page (also shown in the title)
			alert: html/text to be shown in an dismissable alert box above the main content
			html: the content of the page as a string (may contain html)
			page: url to a file containing the content of the page (can be jinja2)
		sidebar (optional) = {html, page, featuredPages, featuredProjects}
			html: text/html that is a custom sidebar
			page: url to a file containing a custom sidebar		featuredPages: list of pages to be automatically shown in the sidebar, item = {img, title, description}
			featuredPages: list of pages to be automatically shown in the sidebar, item = {img, title, description}
			featuredProjects: list of projects to be automatically shown in the sidebar, item = {url, img, title, description}
				url: link target
				img: url to thumbnail
				title: header
				description: short text describing the item
"""
def render_page(siteInfo, pageInfo, sidebarInfo=None):
	if(sidebarInfo is None):
		return render_template("page.html", site=siteInfo, page=pageInfo)
	else:
		return render_template("page.html", site=siteInfo, page=pageInfo, sidebar=sidebarInfo)

def render_page(pageInfo, sidebarInfo=None):
	return render_page(__getSiteInfo(), pageInfo, sidebarInfo)

# renders the page with the standard siteInfo and a sidebar  with featured content (use sidebarInfo=None for no sidebar)
def render_page(pageInfo):
	return render_page(pageInfo, __getFeaturedSidebar())



"""
	Methods for getting the standard siteInfo and sidebar
"""
def __getSiteInfo():
	#Create the standard site info
	return {'name':"Aggrathon", 'header':"Aggrathon.com", 'menu':[{'url':"/", 'title':"Home"},{'url':"/stuff/", 'title':"Stuff"},{'url':"/about/", 'title':"About"},{'url':"/projects/", 'title':"Projects"}]}

def __getFeaturedSidebar():
	#Call methods for getting featured pages and projects
	return {'featuredPages': __featured_sidebar_pages(), 'featuredProjects': __featured_sidebar_projects()}

def __featured_sidebar_pages():
    #Create featured sidebar
    return [{'url':"/project/test/", 'title':'page1', 'description':'hjdfkas afhfsadjfasd asdfjhfdaskhka'}, {'img':"", 'url':"/page/sida/", 'title':'page2', 'description':'hjdfkas afhf sadj fasd asdfjhfd askhka'}]
def __featured_sidebar_projects():
    #Create featured sidebar
	return [{'img':"/static/background.jpg", 'url':"/stuff/", 'title':'poject1', 'description':'hjdfkas afhfsadjfasd asdfjhfdaskhka'}, {'img':"", 'url':"/projects/", 'title':'asd assad jkd as sdajahsd kjdh', 'description':'hjdfkas afhf sadj fasd asdfjhfd askhka klas a asdklj daskas kdjsad jasöljd skaljas kjdkasj das djkljd klas djas'}]



"""
	Simple Methods for rendering pages
"""
#Pages with standard sidebar
def show_page_html(title, html):
	return render_page({'title':title, 'html':html})
def show_page_html(title, html, alert):
	return render_page({'title':title, 'alert':alert, 'html':html})

def show_page_file(title, file):
	return render_page({'title':title, 'page':file})
def show_page_file(title, file, alert):
	return render_page({'title':title, 'alert':alert, 'page':file})

#Pages with no sidebar
def show_page_html_nosidebar(title, html):
	return render_page({'title':title, 'html':html}, None)
def show_page_html_nosidebar(title, html, alert):
	return render_page({'title':title, 'alert':alert, 'html':html}, None)

def show_page_file_nosidebar(title, file):
	return render_page({'title':title, 'page':file}, None)
def show_page_file_nosidebar(title, file, alert):
	return render_page({'title':title, 'alert':alert, 'page':file}, None)

#Pages with custom sidebar
def show_page_html_sidebar_html(title, html, sidebar):
	return render_page({'title':title, 'html':html}, {'html':sidebar})
def show_page_html_sidebar_html(title, html, alert, sidebar):
	return render_page({'title':title, 'alert':alert, 'html':html}, {'html':sidebar})

def show_page_file_sidebar_html(title, file, sidebar):
	return render_page({'title':title, 'page':file}, {'html':sidebar})
def show_page_file_sidebar_html(title, file, alert, sidebar):
	return render_page({'title':title, 'alert':alert, 'page':file}, {'html':sidebar})

def show_page_html_sidebar_file(title, html, sidebar):
	return render_page({'title':title, 'html':html}, {'page':sidebar})
def show_page_html_sidebar_file(title, html, alert, sidebar):
	return render_page({'title':title, 'alert':alert, 'html':html}, {'page':sidebar})

def show_page_file_sidebar_file(title, file, sidebar):
	return render_page({'title':title, 'page':file}, {'page':sidebar})
def show_page_file_sidebar_file(title, file, alert, sidebar):
	return render_page({'title':title, 'alert':alert, 'page':file}, {'page':sidebar})
