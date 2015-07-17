from flask import abort
from database import *

### SITE ###

def get_menu():
	return Menu.query.all()

def get_site_info():
	site = Site.query.first()
	if(site is None):
		abort(500)
	return {'name':site.name, 'header':site.header, 'language':site.language, 'menu':get_menu()}

def get_stats():
	pages = Page.query.count()
	projects = Project.query.count()
	return {'pages':pages, 'projects':projects}

def set_menu(menu):
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


### PAGES ###

def page_get(path):
	page = Page.query.filter_by(path=path).first()
	if(page is None):
		abort(404)
	return page


def page_list():
	return db.session.query(Page.title.label('title'), Page.path.label('url'), FeaturedPage.page_id.label('featured')).outerjoin(FeaturedPage).all()
	
def page_set(path, title, content, featured=False, priority=0, description="", thumbnail=""):
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


### PAGE EDIT ACTIONS ###

def page_action_edit(path, data):
	try:
		title = data['title']
		content = data['content']
		featured = data['featured']
		priority = data['priority']
		description = data['description']
		thumbnail = data['thumbnail']
		page_set(page, title, content, featured, priority, description, thumbnail)
	except KeyError as e:
		return e.message
	return 'success'

def page_action_delete(path):
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

def page_action_move(path, newpath):
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

def page_action_copy(path, newpath):
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
		page_set(newpath, page.title, page.content, False, 0, description, thumbnail)
		return 'success'

### FEATURED ###

def featured_pages():
	pages = db.session.query(
		Page.path.label('url'), PageBlurb.description.label('description'), Page.title.label('title'), PageBlurb.image.label('img'))\
		.join(FeaturedPage).filter(FeaturedPage.page_id==Page.id).join(PageBlurb).filter(PageBlurb.page_id==Page.id)\
		.order_by(FeaturedPage.priority).all()
	return pages

def featured_projects():
	projects = db.session.query(
		Project.path.label('url'), ProjectBlurb.description.label('description'), Project.title.label('title'), ProjectBlurb.image.label('img'))\
		.join(FeaturedProject).filter(FeaturedProject.project_id==Project.id).join(ProjectBlurb).filter(ProjectBlurb.project_id==Project.id)\
		.order_by(FeaturedProject.priority).all()
	return projects


### PROJECT EDIT ACTIONS ###


### MESSAGES ###

def message_add(email, subject, message):
	l_email = email.lower()
	l_subject = subject.lower()
	l_message = message.lower()
	for black in MessageBlacklist.query.all():
		if l_email.find(black.text) != -1:
			return
		if l_subject.find(black.text) != -1:
			return
		if l_message.find(black.text) != -1:
			return
	mess = Message(email, subject, message)
	unr = MessageUnread(mess)
	db.session.add(mess)
	db.session.add(unr)
	db.session.commit()
	#Check for numbers of messages and send optional email

def message_unread_count():
	return MessageUnread.query.count()

def message_total_count():
	return Message.query.count()

def message_list(start, amount):
	total = message_total_count()
	if start >= total:
		start = total - amount
	if start < 0:
		start = 0
	list = db.session.query(
		Message.id.label('id'), Message.email.label('email'), Message.subject.label('subject'), Message.message.label('message'),
		MessageUnread.message_id.label('unread')).outerjoin(MessageUnread).offset(start).limit(amount).all()
	return {'messages':list, 'start':start, 'amount':amount, 'total':total}

### MESSAGES ACTIONS ###

def message_action_unread(id):
	mess = Message.query.get(id)
	if mess is not None:
		if MessageUnread.query.get(id) is None:
			db.session.add(MessageUnread(mess))
			db.session.commit()
		return 'success'
	return 'Message not found'

def message_action_read(id):
	unr = MessageUnread.query.get(id)
	if unr is not None:
		db.session.delete(unr)
		db.session.commit()
	return 'success'

def message_action_delete(id):
	mess = Message.query.get(id)
	if mess is not None:
		unr = MessageUnread.query.get(id)
		if unr is not None:
			db.session.delete(unr)
		db.session.delete(mess)
		db.session.commit()
		return 'success'
	return 'Message not found'

def message_action_ban(phrase):
	mb = MessageBlacklist(phrase)
	db.session.add(mb)
	db.session.commit()
	return 'success'

### TESTDATA ###

def create_test_data():
	page_set("/pages/test/", "Test Page 1", "[insert content here]", True, 10, "Description for test page 1", "/static/background.jpg")
	page_set("/pages/test2/", "Test Page 2", "[insert content here]")
	page_set("/pages/test3/", "Test Page 3", "[insert content here]")
	
	proj = Project("/projects/test/", "Test Project 1", "[insert content here]")
	db.session.add(FeaturedProject(proj, 10))
	db.session.add(ProjectBlurb(proj, "Test Project 1 description here", ""))
	db.session.commit();

	message_add("example@not.real", "Test Content", "Remember to remove all test-content on a real site")

def create_default_menu():
	menu = [{'title':"Home", 'target':"/"},
		 {'title':"Pages", 'target':"/pages/"},
		 {'title':"Projects", 'target':"/projects/"},
		 {'title':"Contact", 'target':"/contact/"},
		 {'title':"Admin", 'target':"/admin/"}]
	set_menu(menu)