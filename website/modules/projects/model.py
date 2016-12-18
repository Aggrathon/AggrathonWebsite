from .database import *
from flask import abort, flash, url_for
from flask.json import dumps as jsondump
from model import RETURN_SUCCESS, FLASH_SUCCESS, FLASH_WARNING, FLASH_ERROR

#region PROJECT_GET

def project_get(path):
	project = Project.query.filter_by(path=path).first()
	if(project is None):
		abort(404)
	latest = project.get_latest_version()
	if latest is not None:
		return {"name":project.title, "text":project.text, "images":project.images, "tags":[tag.tag.tag for tag in project.tags], "links":project.links, "files":latest.files, "version":latest.get_version(), "changelog":latest.changelog}
	return {"name":project.title, "text":project.text, "images":project.images, "tags":[tag.tag.tag for tag in project.tags], "links":project.links}

def project_get_admin(path):
	project = db.session.query(Project.title, Project.text, Project.id, Project.thumbnail, Project.description, ProjectFeatured.priority).filter_by(path=path).outerjoin(ProjectFeatured).first()
	if not project:
		return None
	ProjectLast.update(project)
	return {'path':path, "name":project.title, "text":project.text, "thumbnail":project.thumbnail, "description":project.description, "featured":project.priority is not None, "priority":project.priority,\
		"images":[img[0] for img in db.session.query(ProjectImage.image).filter_by(project_id=project.id).all()],\
		"tagged":[tag[1] for tag in db.session.query(ProjectTagged.tag_id, ProjectTag.tag).filter_by(project_id=project.id).join(ProjectTag).all()],\
		"tags":[tag[0] for tag in db.session.query(ProjectTag.tag).all()],\
		"links":db.session.query(ProjectLink.title, ProjectLink.link).filter_by(project_id=project.id).all()}

def project_list(tags=None,order=None):
	projects = None
	if tags is not None and len(tags) is not 0:
		tq = db.session.query(ProjectTag.id).filter(ProjectTag.tag.in_(tags)).subquery()
		pq = db.session.query(ProjectTagged.project_id).join(tq).group_by(ProjectTagged.project_id).subquery()
		projects = db.session.query(Project.id, Project.path, Project.title, Project.description, Project.thumbnail).join(pq).order_by(Project.title).all()
	else:
		projects = db.session.query(Project.id, Project.path, Project.title, Project.description, Project.thumbnail, Project.edited, Project.created).all()
	if order == 'name':
		projects.sort(key=lambda p: p.title)
	elif order == 'updated':
		projects.sort(reverse=True, key=lambda p: p.edited)
	else: #order is 'created'
		projects.sort(reverse=True, key=lambda p: p.created)
	return [{'path':p.path, 'title':p.title, 'description':p.description, 'thumbnail':p.thumbnail, 'tags':[t[0] for t in \
		db.session.query(ProjectTag.tag).join(db.session.query(ProjectTagged.tag_id).filter_by(project_id=p.id).subquery()).all()]} for p in projects]

def project_tags():
	sub = db.session.query(db.func.count(ProjectTagged.project_id).label("count"), ProjectTagged.tag_id).group_by(ProjectTagged.tag_id).subquery()
	return db.session.query(ProjectTag.tag, sub.c.count).outerjoin(sub).order_by(db.desc("count")).all()

def project_list_admin():
	projects = db.session.query(Project.title, Project.path, ProjectFeatured.project_id.label('featured'), ProjectFeatured.priority).outerjoin(ProjectFeatured).all()
	return projects

def project_versions_get(path):
	project = Project.query.filter_by(path=path).first()
	if(project is None):
		flash("Project at %r not found" %path, FLASH_ERROR)
		return {}
	pvs = ProjectVersion.query.order_by(ProjectVersion.major.desc(),ProjectVersion.minor.desc(),ProjectVersion.patch.desc()).all()
	data = {}
	list = []
	for i in pvs:
		id = 'ver%d_%d_%d'%(i.major,i.minor,i.patch)
		data[id] = {'major':i.major, 'minor':i.minor, 'patch':i.patch, 'changelog':i.changelog, 'date':i.date.isoformat(), 'files': [{'title':f.title, 'url':f.url} for f in i.files]}
		list.append({'id':id, 'name':i.get_version()})
	return {'versions':jsondump(data), 'list':list}

def featured():
	projects = db.session.query(
		Project.path.label('path'), Project.description.label('description'), Project.title.label('title'), Project.thumbnail.label('img'))\
		.join(ProjectFeatured).filter(ProjectFeatured.project_id==Project.id).order_by(ProjectFeatured.priority).all()
	if projects and len(projects) > 0:
		return {"title": "Featured Projects", "list": \
			[{'url': url_for('project', project=item.path), 'title': item.title, 'description': item.description, 'img': item.img} for item in projects]}
	else:
		return None

#endregion

#region PROJECT_EDIT

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
		if priority is None:
			priority = 0
		db.session.add( ProjectFeatured(project, priority) )
	counter = 0
	while counter < len(images):
		db.session.add(ProjectImage(project, images[counter]))
		counter += 1
	counter = 0
	while counter < len(link_titles):
		db.session.add(ProjectLink(project, link_titles[counter], link_urls[counter]))
		counter += 1
	project_tags_set(project, tags)
	db.session.commit()
	ProjectLast.update(Project.query.filter_by(path=path).first())
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
		if priority is None:
			priority = 0
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
	link_length = min(len(link_titles), len(link_urls))
	while counter < len(project.links) and counter < link_length:
		project.links[counter].title = link_titles[counter]
		project.links[counter].link = link_urls[counter]
		counter += 1
	while counter < len(project.links):
		db.session.delete(project.links[counter])
		counter += 1
	while counter < link_length:
		db.session.add(ProjectLink(project, link_titles[counter], link_urls[counter]))
		counter += 1
	project_tags_set(project, tags)
	project.set_edited()
	if flash_result:
		flash('Project Saved', FLASH_SUCCESS)

def project_move(path, newpath):
	if db.session.query(Project.path).filter_by(path=newpath).first():
		return "Target path %r already has a project" %newpath
	p = Project.query.filter_by(path=path).first()
	if p:
		p.path = newpath
		p.set_edited()
		return RETURN_SUCCESS
	return "Project '%r' not found" %path
	
def project_versions_set(path, versions):
	project = Project.query.filter_by(path=path).first()
	if(project is None):
		return "Project at '%r' not found" %path
	counter = 0
	for ver in versions:
		pv = ProjectVersion.query.filter_by(project_id=project.id, major=ver['major'], minor=ver['minor'], patch=ver['patch']).first()
		if pv is None:
			project_version_create(project, ver['major'], ver['minor'], ver['patch'], ver['changelog'], ver['date'], ver.get('file_titles'), ver.get('file_urls'))
		else:
			counter += 1
			pv.changelog = ver['changelog']
			pv.set_date(ver['date'])
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
	project.set_edited()

def project_version_set(path, major, minor, patch, changelog, date, file_titles, file_urls, flash_result=True):
	project = Project.query.filter_by(path=path).first()
	if(project is None):
		return "Project at '%r' not found" %path
	pv = ProjectVersion.query.filter_by(project_id=project.id, major=major, minor=minor, patch=patch).first()
	if not pv:
		project_version_create(project, major, minor, patch, changelog, date, file_titles, file_urls)
		project.set_edited()
		if flash_result:
			flash("Version '%d.%d.%d' for project %r at %r created" %(major, minor, patch, project.title, project.path), FLASH_SUCCESS)
	else:
		pv.major = major
		pv.minor = minor
		pv.patch = patch
		pv.changelog = changelog
		project_files_set(pv, file_titles, file_urls)
		if not pv.set_date(date):
			if flash_result:
				flash("Invalid date format (use YYYY-MM-DD)", FLASH_WARNING)
		project.set_edited()
		if flash_result:
			flash("Version %r for project %r at %r saved" %(pv.get_version(), project.title, project.path), FLASH_SUCCESS)
	
def project_version_create(project, major, minor, patch, changelog, date, file_titles, file_urls):
	pv = ProjectVersion(project, major, minor, patch, changelog, date)
	db.session.add(pv)
	project_files_set(pv, file_titles, file_urls)

def project_version_delete(path, major, minor, patch):
	project = db.session.query(Project.id).filter_by(path = path).first();
	if not project:
		return "Project at %r not found" %path
	pv = ProjectVersion.query.filter_by(project_id=project.id, major=major, minor=minor, patch=patch).first()
	if not pv:
		return "Version %d.%d.%d for project at %r not found" %(major, minor, patch, path)
	db.session.delete(pv)
	db.session.commit()
	return RETURN_SUCCESS
		
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
		
def project_tags_create(tag, flash_result=False):
	t = ProjectTag.query.filter_by(tag=tag).first()
	if t is None:
		db.session.add(ProjectTag(tag))
		db.session.commit()
		if flash_result:
			flash("New tag %r created"%tag, FLASH_SUCCESS)
	elif flash_result:
		flash("Tag %r already exists"%tag, FLASH_ERROR)

def project_feature_set(path, featured=False, priority=10):
	project = Project.query.filter_by(path=path).first()
	if not project:
		return "Project not found"
	pf = ProjectFeatured.query.get(project.id)
	if featured:
		if not pf:
			db.session.add(ProjectFeatured(project, priority))
			db.session.commit()
		elif pf.priority != priority:
			pf.priority = priority
			db.session.commit()
	elif pf:
		db.session.delete(pf)
		db.session.commit()
	return RETURN_SUCCESS
		
def project_tags_rename(tag, newtag):
	t = ProjectTag.query.filter_by(tag=newtag).first()
	if t:
		return "New tag already exists"
	t = ProjectTag.query.filter_by(tag=tag).first()
	if not t:
		return "Tag not found"
	t.tag = newtag
	db.session.commit()
	return RETURN_SUCCESS

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
		lat = ProjectLast.query.get(project.id)
		if lat is not None:
			db.session.delete(lat)
		for tag in project.tags:
			db.session.delete(tag)
		db.session.commit()
		db.session.delete(project)
		db.session.commit()
		return RETURN_SUCCESS

#endregion

def create_test_data():
	project_set("test", "Test Project 1", "[insert content here]", "test project", "/static/background.jpg", "test", ["/static/background.jpg"], ["Ludum Dare"], ["http://ludumdare.com/compo/"], True, flash_result=False)
	project_versions_set("test", [{'major':0, 'minor':0, 'patch':0, 'changelog':"", 'date':'2016-01-01'},{'major':99, 'minor':99, 'patch':99, 'changelog':"Feature 1\nFeature 2\nFeature 3\nFeature 4", 'date':'2016-01-01', 'file_titles':['File 1'], 'file_urls':['file.txt']}])
