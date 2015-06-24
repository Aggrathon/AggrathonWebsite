from flask import abort
from database import *

### GETTERS ###

def getMenu():
	return Menu.query.all()

def getSiteInfo():
	site = Site.query.first()
	if(site is None):
		abort(500)
	return {'name':site.name, 'header':site.header, 'language':site.language, 'menu':getMenu()}

def getPage(path):
	page = Page.query.filter_by(path=path).first()
	if(page is None):
		abort(404)
	return page

def getFeaturedPages():
	pages = db.session.query(
		Page.path.label('url'), PageBlurb.description.label('description'), Page.title.label('title'), PageBlurb.image.label('img'))\
		.join(FeaturedPage).filter(FeaturedPage.page_id==Page.id).join(PageBlurb).filter(PageBlurb.page_id==Page.id)\
		.order_by(FeaturedPage.priority).all()
	return pages

def getFeaturedProjects():
	projects = db.session.query(
		Project.path.label('url'), ProjectBlurb.description.label('description'), Project.title.label('title'), ProjectBlurb.image.label('img'))\
		.join(FeaturedProject).filter(FeaturedProject.project_id==Project.id).join(ProjectBlurb).filter(ProjectBlurb.project_id==Project.id)\
		.order_by(FeaturedProject.priority).all()
	return projects

def getStats():
	pages = Page.query.count()
	projects = Project.query.count()
	return {'pages':pages, 'projects':projects}

def getPageList():
	return db.session.query(Page.title.label('title'), Page.path.label('url'), FeaturedPage.page_id.label('featured')).outerjoin(FeaturedPage).all()


### SETTERS ###

def setMenu(menu):
	oldmenu = Menu.query.all()
	curr = 0
	while( curr < len(oldmenu) and curr < len(menu) ):
		oldmenu[curr].title = menu[curr]['title']
		oldmenu[curr].target = menu[curr]['target']
		curr += 1
	while(curr < len(menu)):
		db.session.add(Menu(menu[curr]['title'], menu[curr]['target']))
		curr += 1
	while(curr < len(oldmenu)):
		db.session.delete(oldmenu[curr])
		curr += 1
	db.session.commit()
	
def setPage(path, title, content, featured=False, priority=0, description="", thumbnail=""):
	page = Page.query.filter_by(path=path).first()
	if(page is None):
		page = Page(path, title, content)
		db.session.add(page)
		if(featured):
			db.session.add( FeaturedPage(page, priority) )
			db.session.add( PageBlurb(page, description, thumbnail) )
		elif(description != "" or thumbnail != ""):
			db.session.add( PageBlurb(page, description, thumbnail) )
	else:
		page.path = path
		page.title = title
		page.content = content

		if(featured):
			feature = FeaturedPage.query.get(page.id)
			if(feature is None):
				db.session.add( FeaturedPage(page, priority) )
			else:
				feature.priority = priority
		else:
			feature = FeaturedPage.query.get(page.id)
			if(feature is not None):
				db.session.delete(feature)

		desc = description != ""
		thumb = thumbnail != ""
		blurb = PageBlurb.query.get(page.id)
		if(blurb is None):
			if(desc or thumb or featured):
				db.session.add( PageBlurb(page, description, thumbnail) )
		else:
			if(not desc and not thumb):
				db.session.delete(blurb)
			else:
				blurb.description = description
				blurb.image = thumbnail

	db.session.commit()


### ACTIONS ###

def action_page_edit(path, data):
	try:
		title = data['title']
		content = data['content']
		featured = data['featured']
		priority = data['priority']
		description = data['description']
		thumbnail = data['thumbnail']
		setPage(page, title, content, featured, priority, description, thumbnail)
	except KeyError as e:
		return e.message
	return 'success'

def action_page_delete(path):
	page = Page.query.filter_by(path=path).first()
	if(page is None):
		return 'Page not found'
	else:
		pb = PageBlurb.query.get(page.id)
		if pb is not None:
			db.session.delete(pb)
		fp = FeaturedPage.query.get(page.id)
		if fp is not None:
			db.session.delete(fp)
		db.session.delete(page)
		db.session.commit()
		return 'success'

def action_page_move(path, newpath):
	page = Page.query.filter_by(path=path).first()
	if(page is None):
		return 'Page not found'
	newpage = Page.query.filter_by(path=newpath).first()
	if newpage is not None:
		return 'Target already exists'
	else:
		page.path = newpath
		db.session.commit()
		return 'success'

def action_page_copy(path, newpath):
	page = Page.query.filter_by(path=path).first()
	if(page is None):
		return 'Page not found'
	newpage = Page.query.filter_by(path=newpath).first()
	if newpage is not None:
		return 'Target already exists'
	else:
		description = ''
		thumbnail = ''
		pageblurb = PageBlurb.query.get(page.id)
		if(pageblurb is not None):
			description = pageblurb.description
			thumbnail = pageblurb.image
		setPage(newpath, page.title, page.content, False, 0, description, thumbnail)
		return 'success'


### TESTDATA ###

def createTestData():
	page = Page("/pages/test/", "Test Page 1", "[insert content here]")
	db.session.add(page)
	db.session.add(Page("/pages/test2/", "Test Page 2", "[insert content here]"))
	db.session.add(Page("/pages/test3/", "Test Page 3", "[insert content here]"))
	db.session.add(FeaturedPage(page, 10))
	db.session.add(PageBlurb(page, "Description for test page 1", "/static/background.jpg"))
	
	proj = Project("/projects/test/", "Test Project 1", "[insert content here]")
	db.session.add(FeaturedProject(proj, 10))
	db.session.add(ProjectBlurb(proj, "Test Project 1 description here", ""))

	db.session.commit();

def createDefaultMenu():
	menu = [{'title':"Home", 'target':"/"},
		 {'title':"Pages", 'target':"/pages/"},
		 {'title':"Projects", 'target':"/projects/"},
		 {'title':"Contact", 'target':"/contact/"},
		 {'title':"Admin", 'target':"/admin/"}]
	setMenu(menu)