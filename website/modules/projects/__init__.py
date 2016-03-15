from . import database, model, view
from flask import url_for
import app

__all__ = ["database", "model", "view"]

# Initialize plugin by registring hooks
app.add_hook(app.HOOK_DATABASE_SETUP_CHECK, database.setup)
app.add_hook(app.HOOK_SIDEBAR_FEATURED_LIST, model.featured)
app.add_hook(app.HOOK_ADMIN_SIDEBAR, lambda : (url_for('projects_admin'), 'Projects', [(url_for('projects_create'), 'Create Project'), (url_for('project_tags'), 'Tags')], ''))
app.add_hook(app.HOOK_ADMIN_WIDGET, lambda : (True, "Recent Projects", "modules/projects/admin/widget.html", database.ProjectLast.query.order_by(database.ProjectLast.time.desc()).all()), 2)