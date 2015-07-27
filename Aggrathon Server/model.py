from flask import abort, flash
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
	messages = Message.query.count()
	return {'pages':pages, 'projects':projects, 'messages':messages}

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
	if PagePrivate.query.get(page.id) is not None:
		flash('This Page is Private', 'warning')
	return page

def page_get_admin(path):
	page = db.session.query(
		Page.title.label('title'), Page.content.label('content'), 
		FeaturedPage.page_id.label('featured'), FeaturedPage.priority.label('priority'),
		PageBlurb.image.label('thumbnail'), PageBlurb.description.label('description'),
		PagePrivate.page_id.label('private')
		).filter_by(path=path).outerjoin(FeaturedPage).outerjoin(PageBlurb).outerjoin(PagePrivate).first()
	if(page is None):
		return {}
	return {'header':page.title, 'content':page.content, 'featured':page.featured, 'priority':page.priority, 'thumbnail':page.thumbnail, 'description': page.description, 'private': page.private}


def page_list_admin():
	return db.session.query(Page.title.label('title'), Page.path.label('url'), FeaturedPage.page_id.label('featured'), PagePrivate.page_id.label('private')).outerjoin(FeaturedPage).outerjoin(PagePrivate).all()

def page_check_path(path):
	if path == '/':
		return true
	elif path.find('/pages/') == 0:
		return True
	return False

def page_set(path, title, content, featured=False, priority=0, description="", thumbnail="", private=False, flash_result=True):
	if not page_check_path(path):
		if flash_result:
			flash('Page not Saved: Invalid Path', 'danger')
		return
	page = Page.query.filter_by(path=path).first()
	if(page is None):
		page = Page(path, title, content)
		db.session.add(page)
		if(featured and not private):
			db.session.add( FeaturedPage(page, priority) )
			db.session.add( PageBlurb(page, description, thumbnail) )
		elif(description != "" or thumbnail != ""):
			db.session.add( PageBlurb(page, description, thumbnail) )
		if private:
			db.session.add( PagePrivate(page) )
		db.session.commit()
		if flash_result:
			flash('New Page Created', 'success')
	else:
		page.path = path
		page.title = title
		page.content = content

		if(featured and not private):
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
			if(not desc and not thumb and not featured):
				db.session.delete(blurb)
			else:
				blurb.description = description
				blurb.image = thumbnail
		if private:
			if PagePrivate.query.get(page.id) is None:
				db.session.add( PagePrivate(page) )
		db.session.commit()
		if flash_result:
			flash('Page Saved', 'success')


### PAGE EDIT ACTIONS ###

def page_action_edit(path, data):
	title = data.get('title')
	content = data.get('content')
	featured = data.get('status') == 'featured'
	priority = data.get('priority')
	description = data.get('description')
	thumbnail = data.get('thumbnail')
	private = data.get('status') == 'private'
	page_set(path, title, content, featured, priority, description, thumbnail, private)

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
	if not page_check_path(newpath):
		return 'Invalid Path'
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
	if not page_check_path(newpath):
		return 'Invalid Path'
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
		page_set(newpath, page.title, page.content, False, 0, description, thumbnail, flash_result=False)
		return 'success'

def page_action_create(path):
	if not page_check_path(path):
		return 'Invalid Path'
	newpage = Page.query.filter_by(path=path).first()
	if newpage is not None:
		return 'Page already exists'
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
	if MessageBlacklist.check_message(email):
		if MessageBlacklist.check_message(subject):
			if MessageBlacklist.check_message(message):
				mess = Message(email, subject, message)
				unr = MessageUnread(mess)
				db.session.add(mess)
				db.session.add(unr)
				db.session.commit()
				return 'success'
	return 'blocked'

def message_unread_count():
	return MessageUnread.query.count()

def message_total_count():
	return Message.query.count()

def message_list(start=0, amount=20):
	total = message_total_count()
	if start >= total:
		start = total - amount
	if start < 0:
		start = 0
	list = db.session.query(
		Message.id.label('id'), Message.email.label('email'), Message.subject.label('subject'), Message.message.label('message'),
		MessageUnread.message_id.label('unread'), Message.time.label('time')).outerjoin(MessageUnread).order_by(Message.id.desc()).offset(start).limit(amount).all()
	return {'messages':list, 'start':start+1, 'amount':amount, 'total':total}

def message_blacklist():
	return MessageBlacklist.query.all();

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
	mb = MessageBlacklist.query.get(phrase.casefold())
	if mb is None:
		db.session.add(MessageBlacklist(phrase))
		db.session.commit()
		return 'success'
	return "Phrase already banned"

def message_action_unban(phrase):
	mb = MessageBlacklist.query.get(phrase.casefold())
	if mb is not None:
		db.session.delete(mb)
		db.session.commit()
		return 'success'
	return 'Phrase not found'

def message_action_recheck_all():
	removed = 0
	messages = Message.query.all()
	bl = MessageBlacklist.query.all()
	for mess in messages:
		email = mess.email.casefold()
		subject = mess.subject.casefold()
		message = mess.message.casefold()
		for b in bl:
			if email.find(b.text) != -1:
				message_action_delete(mess.id)
				removed += 1
				break
			if subject.find(b.text) != -1:
				message_action_delete(mess.id)
				removed += 1
				break
			if message.find(b.text) != -1:
				message_action_delete(mess.id)
				removed += 1
				break
	if removed is 1:
		return '1 Message deleted'
	return '%s Messages deleted' %removed

### TESTDATA ###

def create_test_data():
	page_set("/pages/test/", "Test Page 1", "[insert content here]", True, 10, "Description for test page 1", "/static/background.jpg", flash_result=False)
	page_set("/pages/test2/", "Test Page 2", "[insert content here]", flash_result=False)
	page_set("/pages/test3/", "Test Page 3", "[insert content here]", flash_result=False)
	
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

def create_debug_content():
	reset_db()
	create_default_menu()
	create_test_data()
