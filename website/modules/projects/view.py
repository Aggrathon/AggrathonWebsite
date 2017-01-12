from flask import request, flash, redirect, url_for, jsonify, get_flashed_messages
from app import app
from flask_login import login_required
from . import model
from view import render_page, create_page_fromfile, create_sidebar_fromfile, render_page_standard, create_page_admin, render_page_embed_fromfile


#region admin routes

@app.route('/admin/projects/', methods=['GET', 'POST'])
@login_required
def projects_admin():
	return create_page_admin('Projects', 'modules/projects/admin/projects.html', projects=model.project_list_admin())

@app.route('/admin/projects/edit/', methods=['GET', 'POST'])
@login_required
def projects_edit():
	path = request.args.get('path')
	if request.method == 'POST':
		if not path:
			return "Invalid Project"
		action = request.form.get('action')
		if action == 'save':
			title = request.form.get('title')
			if not title:
				return 'Title is missing'
			text = request.form.get('text')
			if not text:
				return 'Text is missing'
			images = request.form.getlist('images[]')
			tags = request.form.get('tags', "")
			featured = request.form.get('featured') == "true"
			priority = request.form.get('priority', 10)
			thumbnail = request.form.get('thumbnail', "")
			description = request.form.get('description', "")
			link_titles = request.form.getlist('link_titles[]')
			link_targets = request.form.getlist('link_targets[]')
			if not thumbnail or not description or not tags:
				flash("It's recommended to have a <b>thumbnail</b>, a <b>description</b> and <b>tags</b> to make navigation easier", "warning")
			model.project_set(path, title, text, description, thumbnail, tags, images, link_titles, link_targets, featured, priority)
			return jsonify(messages=get_flashed_messages(True))
		elif action == 'move':
			return model.project_move(path, request.form.get('target'))
		elif action == 'delete':
			return model.project_delete(path)
		elif action == 'feature':
			return model.project_feature_set(path, True, request.form.get('priority', 10))
		elif action == 'unfeature':
			return model.project_feature_set(path, False)
		else:
			return 'Action not found'
	if not path or path == '' or path == None:
		return projects_create()
	project = model.project_get_admin(path)
	if not project or project is None:
		flash("Saving will create the new project", model.RETURN_SUCCESS)
		project = { 'path': path }
	return render_page(create_page_fromfile('Edit Project %r'%path, 'modules/projects/admin/edit.html', **project), create_sidebar_fromfile('modules/projects/admin/editbar.html'))

@app.route('/admin/projects/create/', methods=['GET'])
@login_required
def projects_create():
	return create_page_admin('Create Project', 'modules/projects/admin/create.html')

@app.route('/admin/projects/tags/', methods=['GET', 'POST'])
@login_required
def project_tags():
	if request.method == 'POST':
		action = request.form.get('action')
		if action:
			tag = request.form.get('tag')
			if action == 'rename':
				if not tag:
					return "No tag to rename"
				newtag = request.form.get('newtag')
				if not newtag:
					return "No new tag"
				if tag == newtag:
					return "New tag same as old"
				return  model.project_tags_rename(tag, newtag)
			elif action == 'delete':
				if tag:
					model.project_tags_delete(tag)
					return model.RETURN_SUCCESS
				else:
					return "No tag to remove"
		else:
			newtag = request.form.get('newtag')
			if newtag:
				model.project_tags_create(newtag, True)
	return create_page_admin('Project Tags', 'modules/projects/admin/tags.html', tags=model.project_tags())

@app.route('/admin/projects/versions/embed/', methods=['GET', 'POST'])
@login_required
def project_versions_embed():
	path = request.args.get('project')
	if request.method == 'POST' and path:
		action = request.form.get('action')
		if action:
			if action == 'delete':
				major = request.form.get('major')
				minor = request.form.get('minor')
				patch = request.form.get('patch')
				return model.project_version_delete(path, major, minor, patch)
		else:
			try:
				major = int(request.form.get('major'))
				minor = int(request.form.get('minor'))
				patch = int(request.form.get('patch'))
				changelog = request.form.get('changelog')
				date = request.form.get('date')
				file_titles = request.form.getlist('file_title')
				file_urls = request.form.getlist('file_target')
				if major is not None and minor is not None and patch is not None and changelog is not None and date:
					model.project_version_set(path, major, minor, patch, changelog, date, file_titles, file_urls)
				else:
					flash("Could not save the version because of missing data:<br />\n%r"%request.form, model.FLASH_ERROR)
				return render_page_embed_fromfile(None, 'modules/projects/admin/versions.html', open_version="%d_%d_%d"%(major,minor,patch), **model.project_versions_get(path))
			except ValueError:
				flash("Invalid format on data (numbers must be integers)", model.FLASH_ERROR)
	elif not path or path == None:
		flash("No project specified", "danger")
	return render_page_embed_fromfile("Versions", 'modules/projects/admin/versions.html', **model.project_versions_get(path))

#endregion

#region frontend routes

@app.route('/projects/')
def projects():
	tags =  request.args.getlist('tag')
	order = request.args.get('sorting')
	title = "Projects"
	if len(tags) > 0:
		if len(tags) == 1:
			title += " (Tag: %s)" %tags[0]
		else:
			title += " (Tags: %s)" %', '.join(tags)
	return render_page(create_page_fromfile(title, 'modules/projects/frontend/projects.html', projects=model.project_list(tags, order)),\
	    create_sidebar_fromfile("modules/projects/frontend/sidebar.html", tags=model.project_tags()), True)

@app.route('/projects/<path:project>/')
def project(project):
	proj = model.project_get(project)
	return render_page_standard(create_page_fromfile(proj['name'], file='modules/projects/frontend/project.html', hide_title=True, page_modules=True, **proj), True)

#endregion