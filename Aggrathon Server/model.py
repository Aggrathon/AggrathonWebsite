from flask import abort, flash, url_for
from werkzeug import secure_filename
from database import *
from app import login_manager, mail
from flask_mail import Message as MailMessage
from flask_login import current_user
import os
from random import SystemRandom
import string

###  UTILITIES  ###

def get_random_code():
	return ''.join(SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(app.config['CODE_LENGTH']))


### SITE ###

def get_menu():
	return Menu.query.all()

def get_site_info():
	site = Site.query.first()
	if(site is None):
		abort(500)
	return {'name':site.name, 'header':site.header, 'language':site.language, 'menu':get_menu()}

def get_site_info_embed():
	return Site.query.first()

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

def set_site_info(name, header, language):
	if name is None:
		name = app.config['WEBSITE_NAME']
	if header is None:
		header = app.config['WEBSITE_HEADER']
	if language is None:
		language = app.config['WEBSITE_LANGUAGE']
	site = Site.query.first()
	if(site is None):
		site = Site(name, header, language)
		db.session.add(site)
	else:
		site.name = name
		site.header = header
		site.language = language
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

def page_list():
	pages = db.session.query(
		Page.path.label('path'), PageBlurb.description.label('description'), Page.title.label('title'), PageBlurb.image.label('img'))\
		.outerjoin(PagePrivate).filter(PagePrivate.page_id==None).outerjoin(PageBlurb).all()
	return pages

def page_list_admin():
	return db.session.query(Page.title.label('title'), Page.path.label('path'), FeaturedPage.page_id.label('featured'), PagePrivate.page_id.label('private')).outerjoin(FeaturedPage).outerjoin(PagePrivate).all()

def page_set(path, title, content, featured=False, priority=0, description="", thumbnail="", private=False, flash_result=True):
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
	if path == '/':
		return 'Can not move the main page'
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
		page_set(newpath, page.title, page.content, False, 0, description, thumbnail, flash_result=False)
		return 'success'

def page_action_check(path):
	page = Page.query.filter_by(path=path).first()
	if page is None:
		return 'No Page Found'
	return 'exists'

### FEATURED ###

def featured_pages():
	pages = db.session.query(
		Page.path.label('path'), PageBlurb.description.label('description'), Page.title.label('title'), PageBlurb.image.label('img'))\
		.join(FeaturedPage).filter(FeaturedPage.page_id==Page.id).join(PageBlurb).filter(PageBlurb.page_id==Page.id)\
		.order_by(FeaturedPage.priority).all()
	return pages

def featured_projects():
	projects = db.session.query(
		Project.path.label('path'), ProjectBlurb.description.label('description'), Project.title.label('title'), ProjectBlurb.image.label('img'))\
		.join(FeaturedProject).filter(FeaturedProject.project_id==Project.id).join(ProjectBlurb).filter(ProjectBlurb.project_id==Project.id)\
		.order_by(FeaturedProject.priority).all()
	return projects


### PROJECT EDIT ACTIONS ###


### FILES ###

def files_check_path(path, flash_errors=True):
	if path.startswith('/'):
		path = path[1:]
	if not os.path.isdir(path):
		if flash_errors:
			flash('Path not found', 'danger')
		return ''
	if path.find('files') != 0:
		if flash_errors:
			flash('Invalid path', 'danger')
		return ''
	if len(path) > 5 and path[5] != '/':
		if flash_errors:
			flash('Invalid path', 'danger')
		return ''
	return path


def files_list(path='files/', filter=None, flash_errors=True):
	path = files_check_path(path)
	if filter:
		filters = filter.split(',')
	if not path:
		path='files/'
		if flash_errors:
			flash('Showing default location', 'warning')
	folders = []
	files = []
	pathsplit = [x for x in path.split('/') if x]
	for name in os.listdir(path):
		if os.path.isdir(os.path.join(path, name)):
			folders.append(name)
		else:
			if filter:
				if name.split('.')[-1:][0] in filters:
					files.append(name)
			else:
				files.append(name)
	return {'path':pathsplit, 'folders':folders, 'files':files}

def files_create_folder(path, name):
	path = files_check_path(path)
	if path:
		name = secure_filename(name)
		fullpath = path+'/'+name
		if not os.path.isdir(fullpath):
			os.makedirs(fullpath)
		return fullpath
	else:
		return ''

def files_save_file(path, file):
	path = files_check_path(path)
	if path:
		try:
			filename = secure_filename(file.filename)
			file.save(os.path.join(path, filename))
		except:
			return False
		return True
	return False


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
				message_forward(mess)
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

def message_action_send(id):
	mess = Message.query.get(id)
	if mess is not None:
		email_send_text(mess.subject, current_user.email, mess.message, mess.email)
		return 'success'
	return 'Message not found'


def message_forward_add(email, type):
	forw = MessageForwarding.query.get(email)
	if forw is None:
		code = get_random_code()
		forw = MessageForwarding(email, type, code)
		db.session.add(forw)
		db.session.commit()
		url = url_for('forwarding_remove', email=email, code=code, _external=True)
		email_send_html(get_site_info()['name']+" - Message Forwarding Confirmation", email, """
		This email has been setup to recieve notifications on messages sent to the site\n<br />
		Click here to unsubscribe: <a href=\""""+url+"\">"+url+"</a>\n<br />")
		flash("Forwarding Email added ("+email+")", "success")
	else:
		forw.type = type
		db.session.commit()
		flash("Forwarding settings changed for "+email, "success")

def message_forward_remove(email):
	forw = MessageForwarding.query.get(email)
	if forw is not None:
		db.session.delete(forw)
		db.session.commit()
		return 'success'
	return "Email not found ("+email+")"

def message_forward_unsubscribe(email, code):
	forw = MessageForwarding.query.get(email)
	if forw is not None:
		if forw.code == code:
			db.session.delete(forw)
			db.session.commit()
			return True
	return False

def message_forward_list():
	return db.session.query(MessageForwarding.email, MessageForwarding.type)

def message_forward(message):
	unr = message_unread_count()
	frwds = MessageForwarding.query.all()
	one = unr == 1
	remind = one or (unr == 5 or (unr < 100 and unr%10 == 0) or unr%100 == 0)
	for frw in frwds:
		if frw.type == 0:
			email_send_text(message.subject, frw.email, message.message, message.email)
		elif (frw.type == 1 and remind) or (frw.type == 2 and one):
			url = url_for('messages', _external=True)
			url2 = url_for('forwarding_remove', email=frw.email, code=frw.code, _external=True)
			email_send_html(get_site_info()['name']+" - Unread messages: "+unr, frw.email, """
			This email has been setup to recieve notifications on messages sent to the site\n<br />\n<br />
			You have """+unr+""" unread messages\n<br />
			Click here to read them: <a href=\""""+url+"\">"+url+"""</a>\n<br />\n<br />\n<br />
			Click here to unsubscribe: <a href=\""""+url2+"\">"+url2+"</a>\n<br />")


### LOGIN ###
@login_manager.user_loader
def login_get_user_by_email(email:str):
	return User.query.get(email)

@login_manager.token_loader
def login_get_user_by_token(token:str):
	return User.query.filter_by(token=token).first()

def login_action_sendcode(email):
	user = User.query.get(email)
	if user is None:
		return "Invalid Email"
	if not user.get_verification_expired():
		return "Verification sent too recently"
	code = get_random_code();
	user.set_verification(code)
	url = url_for('login', email=email, code=code, _external=True)
	urlmain = url_for('main', _external=True)
	message = '<p>A login request has been made at <a href="'+urlmain+'">'+urlmain+'</a></p><p>Click here to login: <a href="'+url+'">'+url+'</a></p><p>If you did not request this login-verification, please ignore this message</p>'
	email_send_html("Login Request - "+app.config["WEBSITE_NAME"], email, message)
	return 'success'

def login_action_ceckcode(email, code):
	user = User.query.get(email)
	if user is None:
		return "Invalid Email"
	if user.verification_time and user.get_verification_expired():
		return "Verification Expired"
	if user.verification_code == '':
		return "New Verification needed"
	if code == user.verification_code:
		user.verification_code = ''
		user.verification_time = None
		db.session.commit()
		return "success"
	else:
		user.verification_code = ''
		return "Invalid Verification"


### EMAIL ###
def email_send_text(subject:str, recipient:str, message:str, sender:str = None):
	subject = subject.replace('\n', ' ')
	if sender is None:
		sender = app.config['MAIL_SENDER_ADRESS']
	email = MailMessage(subject=subject, recipients=[recipient], body=message, sender=sender)
	mail.send(email)
	
def email_send_html(subject:str, recipient:str, message:str, sender:str = None):
	subject = subject.replace('\n', ' ')
	if sender is None:
		sender = app.config['MAIL_SENDER_ADRESS']
	email = MailMessage(subject=subject, recipients=[recipient], html=message, sender=sender)
	mail.send(email)


### TESTDATA ###

def create_test_data():
	page_set("test", "Test Page 1", "[insert content here]", True, 10, "Description for test page 1", "/static/background.jpg", flash_result=False)
	page_set("test2", "Test Page 2", "[insert content here]", flash_result=False)
	page_set("test3", "Test Page 3", "[insert content here]", flash_result=False)
	
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
