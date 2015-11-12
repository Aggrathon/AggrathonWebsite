""" Website Setup Config """
#	Before starting the server look through this file and change configurations if necessary
#	If the server is running, restart it to apply any changes made to this file

"""  DEBUG  """
# These should not be True on any kind of live server
DEBUG = True
LOGIN_DISABLED = True


"""  DATABASE  """
## SQLALCHEMY_DATABASE_URI Pattern:
#    servertype://username:password@server:port/database
## Documentation:
#    http://docs.sqlalchemy.org/en/rel_1_0/core/engines.html
## Examples: 
#    mysql://user:pass@localhost/mydatabase
#    sqlite:///path/to/foo.db
SQLALCHEMY_DATABASE_URI = "sqlite:///database.db"
## Database Schema error
#	At startup the database is checked for matching tables
#	What should happen if the tables aren't mathing:
#	'RESET': Empty the whole database and recreate the needed tables (Should be used at the first startup)
#	'NOTHING': An error is shown, but nothing is done about it
DATABASE_SCHEMA_ERROR_ACTION = 'RESET'


"""  DEFAULTS  """
## Default values are used if no other value is set
#	These values can later be set in the website settings
#	The admin email is however important to change to be able to login
WEBSITE_NAME = 'Website'
WEBSITE_HEADER = 'Website'
WEBSITE_LANGUAGE = 'en'
WEBSITE_MENU = [
	{'title':'Home',  'target':'/'},
	{'title':'Pages',  'target':'/pages/'},
	{'title':'Projects',  'target':'/projects/'},
	{'title':'Contact',  'target':'/contact/'},
	{'title':'Admin',  'target':'/admin/'}
	]
WEBSITE_ADMIN = ['admin@example.com']


"""  EMAIL  """
## If not using LOGIN_DISABLED email is needed to login
MAIL_SERVER = 'localhost'
MAIL_PORT = 25
MAIL_USE_TLS = False
MAIL_USE_SSL = False
MAIL_USERNAME = None
MAIL_PASSWORD = None
MAIL_SENDER_ADRESS = 'admin@example.com'


"""  CONTACT  """
## Get ReCaptcha key here https://www.google.com/recaptcha/
RECAPTCHA_ENABLED = True
RECAPTCHA_SITE_KEY = ""
RECAPTCHA_SECRET_KEY = ""


"""  SECURITY  """
## SECRET_KEY is used for sessions
import os
SECRET_KEY = os.urandom(24)


"""  EXTERNAL HTML LIBRARIES  """
## Config:
#	Bootstrap: parent directory
#	JQuery: actual script
#	Editor: actual script for a rich-text-editor (eg CKEditor)
#	Editor Config: config and init (TEXTAREA_ID is the selector for the replaced textarea)
#	Editor js Insert: js for inserting html to the texteditor (TEXTAREA_ID: selector for area, INSERT_HTML: is replaced by the html to insert)
## Official CDNs:
#BOOTSTRAP = 'https://maxcdn.bootstrapcdn.com/bootstrap/3.3.5/'
#JQUERY = 'https://ajax.googleapis.com/ajax/libs/jquery/1.11.3/jquery.min.js'
#EDITOR = '//cdn.ckeditor.com/4.5.1/standard/ckeditor.js'
## Local files:
BOOTSTRAP = '/static/external/bootstrap-3.3.5/'
JQUERY = '/static/external/jquery-1.11.3.min.js'
EDITOR = '/static/external/CKEditor/custom-4.5.1/ckeditor.js'
EDITOR_CONFIG = """CKEDITOR.replace('TEXTAREA_ID', { customConfig: '/static/external/CKEditor/config/config.js' }); CKEDITOR.dtd.$removeEmpty['span'] = false;"""
EDITOR_JS_INSERT = "CKEDITOR.instances['TEXTAREA_ID'].insertHtml(INSERT_HTML);"