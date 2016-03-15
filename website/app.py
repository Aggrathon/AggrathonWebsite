from flask import Flask
from flask_login import LoginManager
from flask_mail import Mail
from flask_recaptcha import ReCaptcha
import os

app = Flask(__name__)
app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True
app.config.from_pyfile("config.py")

login_manager = LoginManager(app)
mail = Mail(app)
recaptcha = ReCaptcha(app=app)


# Make the WSGI interface available at the top level so wfastcgi can get it.
wsgi_app = app.wsgi_app


#region hooks
"""
	This is the central point in the application where modules can register callbacks for events (rendering or otherwise)
	The implementation is a dictionary (with strings as keys) that holds lists of functions 
"""
hook_manager = dict()
def add_hook(type:str, func, index:int = 9999):
	hook = hook_manager.get(type)
	if not hook:
		hook_manager[type] = [func]
	else:
		hook.insert(index, func)

def get_hook(type:str):
	return hook_manager.get(type, [])

### STANDARD HOOKS ###
HOOK_SIDEBAR_FEATURED_LIST = "featured_sidebar_list"
HOOK_DATABASE_SETUP_CHECK = "database_setup_check"
HOOK_DATABASE_CREATE = "database_create"
HOOK_DATABASE_RESET = "database_reset"
HOOK_ADMIN_SIDEBAR = "admin_sidebar"
HOOK_ADMIN_WIDGET = "admin_widget"
HOOK_ADMIN_BUTTONS = "admin_buttons"
HOOK_TEST_CONTENT = "create_test_content"

import database
add_hook(HOOK_DATABASE_CREATE, database.create_self)
add_hook(HOOK_DATABASE_RESET, database.reset_self)
add_hook(HOOK_DATABASE_SETUP_CHECK, database.setup_self)
import model
add_hook(HOOK_SIDEBAR_FEATURED_LIST, model.featured_pages)


#endregion

# Init all scripts
import routes
from modules import *

#Check database
database.setup_db()
