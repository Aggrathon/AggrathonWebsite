import app
from flask import url_for
from . import database, model, view

__all__ = ["database", "model", "view"]


# Initialize hooks
app.add_hook(app.HOOK_DATABASE_SETUP_CHECK, database.check_setup)
app.add_hook(app.HOOK_TEST_CONTENT, model.create_test_data)
app.add_hook(app.HOOK_ADMIN_BUTTONS, model.message_admin_button)
app.add_hook(app.HOOK_ADMIN_SIDEBAR, lambda : (url_for('messages'), 'Messages', [(url_for('blacklist'), 'Blacklist'),(url_for('forwarding'), 'Forwarding')], str(model.message_unread_count())), 2)