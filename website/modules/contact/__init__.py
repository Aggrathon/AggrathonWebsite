__all__ = ["database", "model", "view"]

import app
from flask import url_for
from modules.contact import database, model, view


# Initialize hooks
app.add_hook(app.HOOK_DATABASE_SETUP_CHECK, database.check_setup)
app.add_hook(app.HOOK_TEST_CONTENT, model.create_test_data)
app.add_hook(app.HOOK_ADMIN_BUTTONS, model.message_admin_button)
app.add_hook(app.HOOK_ADMIN_SIDEBAR, lambda : (url_for('messages'), 'Messages', [(url_for('blacklist'), 'Blacklist'),(url_for('forwarding'), 'Forwarding')], str(model.message_unread_count())), 2)
app.add_hook(app.HOOK_EDIT_CONTENT, model.edit_callbak)
