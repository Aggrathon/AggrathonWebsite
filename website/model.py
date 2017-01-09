from flask import abort, flash, url_for, redirect
from flask.json import dumps as jsondump
from werkzeug import secure_filename
from database import *
from app import login_manager, mail, get_hook, HOOK_ADMIN_WIDGET, HOOK_TEST_CONTENT, HOOK_ADMIN_BUTTONS
from flask_mail import Message as MailMessage
from flask_login import current_user
import os
from random import SystemRandom
import string


### CONSTANTS ###
RETURN_SUCCESS = 'success'

FLASH_SUCCESS = 'success'
FLASH_WARNING = 'warning'
FLASH_ERROR = 'danger'

###  UTILITIES  ###

def get_random_code():
	return ''.join(SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(app.config['CODE_LENGTH']))


#region SITE

def get_menu():
	return Menu.query.all()

def get_site_info(editable=False):
	site = Site.query.first()
	if(site is None):
		abort(500)
	if (current_user.is_authenticated or app.config.get('LOGIN_DISABLED')):
		buttons = []
		for b in get_hook(HOOK_ADMIN_BUTTONS):
			button = b()
			if button:
				buttons.append(button)
		return {'name':site.name, 'header':site.header, 'language':site.language, 'menu':get_menu(), 'admin':{'buttons':buttons, 'edit':editable}}
	return {'name':site.name, 'header':site.header, 'language':site.language, 'menu':get_menu()}

def get_site_info_embed():
	return Site.query.first()

def get_admin_widgets():
	widgets = [(True, "Recent Pages", "admin/pages/widget.html", PageLast.query.order_by(PageLast.time.desc()).all())]
	for w in get_hook(HOOK_ADMIN_WIDGET):
		result = w()
		if result:
			widgets.append(result)
	return widgets

def set_menu(titles, targets):
	oldmenu = Menu.query.all()
	if len(oldmenu) == len(titles):
		same = True
		for index, val in enumerate(oldmenu):
			if val.title != titles[index] or val.target != targets[index]:
				same = False
				break
		if same:
			return False
	curr = 0
	while( curr < len(oldmenu) and curr < len(titles) ):
		oldmenu[curr].title = titles[curr]
		oldmenu[curr].target = targets[curr]
		curr += 1
	while(curr < len(titles)):
		db.session.add(Menu(titles[curr], targets[curr]))
		curr += 1
	while(curr < len(oldmenu)):
		db.session.delete(oldmenu[curr])
		curr += 1
	db.session.commit()
	return True

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

def get_user_list():
	return db.session.query(User.email).all()

def set_user_list(list):
	usrs = User.query.all()
	matched = []
	for usr in usrs:
		if usr.email not in list:
			db.session.delete(usr)
		else:
			matched.append(usr.email)
	if len(usrs) == len(list) == len(matched):
		return True
	for email in list:
		if email not in matched:
			if len(email.split('@')) == 2 and len(email.split('@')[1].split('.')) > 1:
				matched.append(email)
				db.session.add(User(email))
			else:
				flash('\''+email+'\' is not a valid email', FLASH_ERROR)
	if len(matched) > 0:
		flash("Administrators changed", FLASH_SUCCESS)
		db.session.commit()
		return True
	else:
		session.rollback()
		return False

#endregion


#region PAGES

def page_get(path):
	page = Page.query.filter_by(path=path).first()
	if(page is None):
		abort(404)
	if PagePrivate.query.get(page.id) is not None:
		flash('This Page is Private', FLASH_WARNING)
	return page

def page_get_admin(path):
	page = Page.query.filter_by(path=path).first()
	if(page is None):
		return {}
	ret = {'header':page.title, 'content':page.content }
	blurb = PageBlurb.query.get(page.id)
	if blurb:
		ret['thumbnail'] = blurb.image
		ret['description'] = blurb.description
	featured = FeaturedPage.query.get(page.id)
	if featured:
		ret['featured'] = True
		ret['priority'] = featured.priority
	private = PagePrivate.query.get(page.id)
	if private:
		ret['private'] = True
	PageLast.update(page)
	return ret

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
			flash('New Page Created', FLASH_SUCCESS)
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
			flash('Page Saved', FLASH_SUCCESS)

#endregion

#region PAGE_EDIT_ACTIONS

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
		lp = LastPage.query.get(page.id)
		if lp is not None:
			db.session.delete(lp)
		db.session.delete(page)
		db.session.commit()
		return RETURN_SUCCESS

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
		return RETURN_SUCCESS

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
		return RETURN_SUCCESS

def page_action_check(path):
	page = Page.query.filter_by(path=path).first()
	if page is None:
		return 'No Page Found'
	return 'exists'

def page_edit_callback(path):
	if path == "/":
		return redirect(url_for('pages_edit', page=path), 303)
	elif path == "/pages/":
		return redirect(url_for('pages_admin'), 303)
	elif path.startswith("/pages/"):
		return redirect(url_for('pages_edit', page=path.split('/pages/', 1)[1][:-1]), 303)
	return None

#endregion


#region FEATURED

def featured_pages():
	pages = db.session.query(
		Page.path.label('path'), PageBlurb.description.label('description'), Page.title.label('title'), PageBlurb.image.label('img'))\
		.join(FeaturedPage).filter(FeaturedPage.page_id==Page.id).join(PageBlurb).filter(PageBlurb.page_id==Page.id)\
		.order_by(FeaturedPage.priority).all()
	if pages and len(pages) > 0:
		return {"title": "Featured Pages", "list": \
			[{'url': url_for('page', page=item.path), 'title': item.title, 'description': item.description, 'img': item.img} for item in pages]}
	else:
		return None

#endregion


#region FILES

def files_check_path(path, flash_errors=True):
	if path.startswith('/'):
		path = path[1:]
	if not os.path.isdir(path):
		if flash_errors:
			flash('Path not found', FLASH_ERROR)
		return ''
	if path.find('files') != 0:
		if flash_errors:
			flash('Invalid path', FLASH_ERROR)
		return ''
	if len(path) > 5 and path[5] != '/':
		if flash_errors:
			flash('Invalid path', FLASH_ERROR)
		return ''
	return path


def files_list(path='files/', filter=None, flash_errors=True):
	path = files_check_path(path)
	if filter:
		filters = filter.split(',')
	if not path:
		path='files/'
		if flash_errors:
			flash('Showing default location', FLASH_WARNING)
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
			os.makedirs(fullpath, exist_ok=True)
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

#endregion


#region LOGIN
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
	return RETURN_SUCCESS

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
		return RETURN_SUCCESS
	else:
		user.verification_code = ''
		return "Invalid Verification"

#endregion


#region EMAIL

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

#endregion


#region TESTDATA

def create_test_data():
	page_set("test", "Test Page 1", "[insert content here]", True, 10, "Description for test page 1", "/static/background.jpg", flash_result=False)
	page_set("test2", "Test Page 2", "[insert content here]", flash_result=False)
	page_set("test3", "Test Page 3", "[insert content here]", flash_result=False)
	for create in get_hook(HOOK_TEST_CONTENT):
		create()

def create_default_menu():
	titles  = ["Home",	"Pages",	"Projects",		"Contact"]
	targets = ["/",		"/pages/",	"/projects/",	"/contact/"]
	set_menu(titles, targets)

def create_debug_content():
	reset_db()
	create_default_menu()
	create_test_data()

#endregion
