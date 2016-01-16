from flask import abort, flash, url_for
from werkzeug import secure_filename
from database import *
from app import login_manager, mail
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


### SITE ###

def get_menu():
	return Menu.query.all()

def get_site_info(editable=False):
	site = Site.query.first()
	if(site is None):
		abort(500)
	if (current_user.is_authenticated or app.config.get('LOGIN_DISABLED')):
		return {'name':site.name, 'header':site.header, 'language':site.language, 'menu':get_menu(), 'admin':{'unread':message_unread_count(), 'edit':editable}}
	return {'name':site.name, 'header':site.header, 'language':site.language, 'menu':get_menu()}

def get_site_info_embed():
	return Site.query.first()

def get_admin_front():
	pages = LastPage.query.order_by(LastPage.time.desc()).all()
	projects = ProjectLast.query.order_by(ProjectLast.time.desc()).all()
	notes = Text.query.get('ADMIN_NOTES')
	if notes:
		return {'pages':pages, 'projects':projects, 'notes':notes.text}
	else:
		return {'pages':pages, 'projects':projects}

def set_admin_notes(notes):
	dbn = Text.query.get('ADMIN_NOTES')
	if dbn:
		if notes == "":
			db.session.delete(dbn)
		else:
			dbn.text = notes
		db.session.commit()
	elif notes != "":
		db.session.add(Text('ADMIN_NOTES', notes))
		db.session.commit()
	return RETURN_SUCCESS

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


### PAGES ###

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
	last = LastPage.query.get(page.id)
	if last is None:
		if LastPage.query.count() >= 5:
			db.session.delete(LastPage.query.order_by('time').first())
		db.session.add(LastPage(page))
	else:
		last.update()
	db.session.commit()
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

### FEATURED ###

def featured_pages():
	pages = db.session.query(
		Page.path.label('path'), PageBlurb.description.label('description'), Page.title.label('title'), PageBlurb.image.label('img'))\
		.join(FeaturedPage).filter(FeaturedPage.page_id==Page.id).join(PageBlurb).filter(PageBlurb.page_id==Page.id)\
		.order_by(FeaturedPage.priority).all()
	return pages

def featured_projects():
	projects = db.session.query(
		Project.path.label('path'), Project.description.label('description'), Project.title.label('title'), Project.thumbnail.label('img'))\
		.join(ProjectFeatured).filter(ProjectFeatured.project_id==Project.id).order_by(ProjectFeatured.priority).all()
	return projects


### PROJECT GET ###

def project_get(path):
	project = Project.query.filter_by(path=path).first()
	if(project is None):
		abort(404)
	files = ProjectVersion.query.filter_by(project=project, major=0, minor=0, patch=0).first().files
	latest = project.get_latest_version()
	if latest is not None:
		return {"name":project.title, "text":project.text, "images":project.images, "tags":[tag.tag.tag for tag in project.tags], "links":project.links, "files":files + latest.files, "version":latest.get_version(), "changelog":latest.changelog}
	return {"name":project.title, "text":project.text, "images":project.images, "tags":[tag.tag.tag for tag in project.tags], "links":project.links, "files":files}

def project_list(tags=None,order=None):
	projects = None
	if tags is not None and len(tags) is not 0:
		tq = db.session.query(ProjectTag.id).filter(ProjectTag.tag.in_(tags)).subquery()
		pq = db.session.query(ProjectTagged.project_id).join(tq).group_by(ProjectTagged.project_id).subquery()
		projects = db.session.query(Project.id, Project.path, Project.title, Project.description, Project.thumbnail).join(pq).order_by(Project.title).all()
	else:
		projects = db.session.query(Project.id, Project.path, Project.title, Project.description, Project.thumbnail).all()
	if order == 'name':
		projects.sort(key=lambda p: p.title)
	elif order == 'updated':
		pass
	else: #order is 'created'
		pass
	return [{'path':p.path, 'title':p.title, 'description':p.description, 'thumbnail':p.thumbnail, 'tags':[t[0] for t in \
		db.session.query(ProjectTag.tag).join(db.session.query(ProjectTagged.tag_id).filter_by(project_id=p.id).subquery()).all()]} for p in projects]

def project_tags():
	return db.session.query(db.func.count(ProjectTagged.project_id).label("count"), ProjectTag.tag).group_by(ProjectTagged.tag_id).join(ProjectTag).order_by(db.desc("count")).all()

def project_list_admin():
	projects = db.session.query(Project.title, Project.path, ProjectFeatured.project_id.label('featured')).outerjoin(ProjectFeatured).all()
	return projects

### PROJECT EDIT ###

def project_set(path, title, text, description, thumbnail, tags, images, link_titles, link_urls, featured=False, priority=0, private=False, flash_result=True):
	project = Project.query.filter_by(path=path).first()
	if(project is None):
		project_create(path, title, text, description, thumbnail, tags, images, link_titles, link_urls, featured, priority, private, flash_result)
	else:
		project_update(project, title, text, description, thumbnail, tags, images, link_titles, link_urls, featured, priority, private, flash_result)

def project_create(path, title, text, description, thumbnail, tags, images, link_titles, link_urls, featured=False, priority=0, private=False, flash_result=True):
	project = Project(path, title, text, description, thumbnail)
	db.session.add(project)
	if(featured and not private):
		db.session.add( ProjectFeatured(project, priority) )
	counter = 0
	while counter < len(images):
		db.session.add(ProjectImage(project, images[counter]))
		counter += 1
	counter = 0
	while counter < len(link_titles):
		db.session.add(ProjectLink(project, link_titles[counter], link_urls[counter]))
		counter += 1
	db.session.add(ProjectVersion(project, 0, 0, 0))
	project_tags_set(project, tags)
	db.session.commit()
	if flash_result:
		flash('New Project Created', FLASH_SUCCESS)
		
def project_update(project, title, text, description, thumbnail, tags, images, link_titles, link_urls, featured=False, priority=0, private=False, flash_result=True):
	project.title = title
	project.text = text
	project.description = description
	project.thumbnail = thumbnail
	#featured
	feat = ProjectFeatured.query.get(project.id)
	if(featured and not private):
		if(feat is None):
			db.session.add(ProjectFeatured(project, priority))
		else:
			feat.priority = priority
	elif(feat is not None):
		db.session.delete(feat)
	#images
	counter = 0
	while counter < len(project.images) and counter < len(images):
		project.images[counter].image = images[counter]
		counter += 1
	while counter < len(project.images):
		db.session.delete(project.images[counter])
		counter += 1
	while counter < len(images):
		db.session.add(ProjectImage(project, images[counter]))
		counter += 1
	#links
	counter = 0
	while counter < len(project.links) and counter < len(link_titles):
		project.links[counter].title = link_titles[counter]
		project.links[counter].link = link_urls[counter]
		counter += 1
	while counter < len(project.links):
		db.session.delete(project.links[counter])
		counter += 1
	while counter < len(link_titles):
		db.session.add(ProjectLink(project, link_titles[counter], link_urls[counter]))
		counter += 1
	project_tags_set(project, tags)
	db.session.commit()
	if flash_result:
		flash('Project Updated', FLASH_SUCCESS)

def project_move(path, newpath):
	if db.session.query(Project.path).filter_by(path=newpath).first():
		return "Target path %r already has a project" %newpath
	p = Project.query.filter_by(path=path).first()
	if p:
		p.path = newpath
		db.session.commit()
		return RETURN_SUCCESS
	return "Project '%r' not found" %path
	
def project_version_set(path, versions):
	project = Project.query.filter_by(path=path).first()
	if(project is None):
		return "Project '%r' not found" %path
	counter = 0
	for ver in versions:
		pv = ProjectVersion.query.filter_by(project_id=project.id, major=ver['major'], minor=ver['minor'], patch=ver['patch']).first()
		if pv is None:
			project_version_create(project, ver['major'], ver['minor'], ver['patch'], ver['changelog'], ver.get('file_titles'), ver.get('file_urls'))
		else:
			counter += 1
			pv.changelog = ver['changelog']
			project_files_set(pv, ver.get('file_titles'), ver.get('file_urls'))
	if counter < len(project.versions):
		for ver in project.versions:
			delete = True
			for v in versions:
				if ver.major == v['major'] and ver.minor == v['minor'] and ver.patch == v['patch']:
					delete = False
					break
			if delete:
				db.session.delete(ver)
	db.session.commit()
	
def project_version_create(project, major, minor, patch, changelog, file_titles, file_urls):
	pv = ProjectVersion(project, major, minor, patch, changelog)
	db.session.add(pv)
	project_files_set(pv, file_titles, file_urls)
		
def project_files_set(version, titles, urls):
	if titles is None:
		for file in version.files:
			db.session.delete(file)
		return
	counter = 0
	while counter < len(version.files) and counter < len(titles):
		version.files[counter].title = titles[counter]
		version.files[counter].url = urls[counter]
		counter += 1
	while counter < len(version.files):
		db.session.delete(version.files[counter])
		counter += 1
	while counter < len(titles):
		db.session.add(ProjectFile(version, titles[counter], urls[counter]))
		counter += 1

def project_tags_set(project, tags):
	if tags is None or tags is "":
		for tag in project.tags:
			db.session.delete(tag)
		return
	taglist = [x.strip() for x in tags.split(',')]
	for tag in project.tags:
		if tag.tag.tag not in taglist:
			db.session.delete(tag.tag)
	for t in taglist:
		tag = ProjectTag.query.filter_by(tag=t).first()
		if tag is None:
			tag = ProjectTag(t)
			db.session.add(tag)
			db.session.add(ProjectTagged(project, tag))
		else:
			tagged = ProjectTagged.query.filter_by(project=project, tag=tag).first()
			if tagged is None:
				db.session.add(ProjectTagged(project, tag))
		
def project_tags_create(tag):
	t = ProjectTag.query.filter_by(tag=tag).first()
	if t is None:
		db.session.add(ProjectTag(tag))
		db.session.commit()

def project_tags_delete(tag):
	t = ProjectTag.query.filter_by(tag=tag).first()
	if t is not None:
		for p in t.projects:
			db.session.delete(p)
		db.session.delete(t)
		db.session.commit()

def project_delete(path):
	project = Project.query.filter_by(path=path).first()
	if(project is None):
		return 'Could not find project to delete (%r)' %path
	else:
		for img in project.images:
			db.session.delete(img)
		for link in project.links:
			db.session.delete(link)
		for version in project.versions:
			for file in version.files:
				db.session.delete(file)
			db.session.delete(version)
		feat = ProjectFeatured.query.get(project.id)
		if feat is not None:
			db.session.delete(feat)
		for tag in project.tags:
			db.session.delete(tag)
		db.session.commit()
		db.session.delete(project)
		db.session.commit()
		return RETURN_SUCCESS


### FILES ###

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
				return RETURN_SUCCESS
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
		return RETURN_SUCCESS
	return 'Message not found'

def message_action_read(id):
	unr = MessageUnread.query.get(id)
	if unr is not None:
		db.session.delete(unr)
		db.session.commit()
	return RETURN_SUCCESS

def message_action_delete(id):
	mess = Message.query.get(id)
	if mess is not None:
		unr = MessageUnread.query.get(id)
		if unr is not None:
			db.session.delete(unr)
		db.session.delete(mess)
		db.session.commit()
		return RETURN_SUCCESS
	return 'Message not found'

def message_action_ban(phrase):
	mb = MessageBlacklist.query.get(phrase.casefold())
	if mb is None:
		db.session.add(MessageBlacklist(phrase))
		db.session.commit()
		return RETURN_SUCCESS
	return "Phrase already banned"

def message_action_unban(phrase):
	mb = MessageBlacklist.query.get(phrase.casefold())
	if mb is not None:
		db.session.delete(mb)
		db.session.commit()
		return RETURN_SUCCESS
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
		return RETURN_SUCCESS
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
		flash("Forwarding Email added ("+email+")", FLASH_SUCCESS)
	else:
		forw.type = type
		db.session.commit()
		flash("Forwarding settings changed for "+email, FLASH_SUCCESS)

def message_forward_remove(email):
	forw = MessageForwarding.query.get(email)
	if forw is not None:
		db.session.delete(forw)
		db.session.commit()
		return RETURN_SUCCESS
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
			email_send_html(get_site_info()['name']+" - Unread messages: "+str(unr), frw.email, """
			This email has been setup to recieve notifications on messages sent to the site\n<br />\n<br />
			You have """+str(unr)+""" unread messages\n<br />
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
	
	project_set("test", "Test Project 1", "[insert content here]", "test project", "/static/background.jpg", "test", ["/static/background.jpg"], ["Ludum Dare"], ["http://ludumdare.com/compo/"], True, flash_result=False)
	project_version_set("test", [{'major':0, 'minor':0, 'patch':0, 'changelog':""},{'major':99, 'minor':99, 'patch':99, 'changelog':"Feature 1\nFeature 2\nFeature 3\nFeature 4", 'file_titles':['File 1'], 'file_urls':['file.txt']}])

	message_add("example@not.real", "Test Content", "Remember to remove all test-content on a real site")

def create_default_menu():
	titles  = ["Home",	"Pages",	"Projects",		"Contact"]
	targets = ["/",		"/pages/",	"/projects/",	"/contact/"]
	set_menu(titles, targets)

def create_debug_content():
	reset_db()
	create_default_menu()
	create_test_data()
