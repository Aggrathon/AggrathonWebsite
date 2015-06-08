from flask import render_template

def show_page(title=None, alert=None, html=None, page=None, sidebarhtml=None, sidebarpage=None, featuredSidebar=True):
    args = { 'featuredSidebar': featuredSidebar }
    if(title is not None):
        args['title'] = title
    if(alert is not None):
        args['alert'] = alert
    if(html is not None):
        args['html'] = html
    if(page is not None):
        args['page'] = page
    if(sidebarhtml is not None):
        args['sidebarhtml'] = sidebarhtml
    if(sidebarpage is not None):
        args['sidebarpage'] = sidebarpage
    return render_page(**args)

def render_page(**options):
	featured = options.get('featuredSidebar')
	if(featured is None or featured is True):
		sidebarFeaturedPages=featured_sidebar_pages()
		sidebarFeaturedProjects=featured_sidebar_projects()
		return render_template("page_sidebar.html", sidebarFeaturedPages=sidebarFeaturedPages, sidebarFeaturedProjects=sidebarFeaturedProjects, **options)
	elif(options.get("sidebarhtml") != None or options.get("sidebarpage") != None):
		return render_template("page_sidebar.html", **options)
	else:
		return render_template("page_base.html", **options)

def featured_sidebar_pages():
    #Create featured sidebar
    return [{'url':"/project/test/", 'title':'page1', 'description':'hjdfkas afhfsadjfasd asdfjhfdaskhka'}, {'img':"", 'url':"/page/sida/", 'title':'page2', 'description':'hjdfkas afhf sadj fasd asdfjhfd askhka'}]
def featured_sidebar_projects():
    #Create featured sidebar
	return [{'img':"/static/background.jpg", 'url':"/stuff/", 'title':'poject1', 'description':'hjdfkas afhfsadjfasd asdfjhfdaskhka'}, {'img':"", 'url':"/projects/", 'title':'asd assad jkd as sdajahsd kjdh', 'description':'hjdfkas afhf sadj fasd asdfjhfd askhka klas a asdklj daskas kdjsad jasöljd skaljas kjdkasj das djkljd klas djas'}]