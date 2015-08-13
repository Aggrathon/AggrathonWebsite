### Website Setup Config ###

###  DEBUG  ###
# These should not be True on any kind of live server
DEBUG = True
LOGIN_DISABLED = True


###  DATABASE  ###
## SQLALCHEMY_DATABASE_URI Pattern:
#    servertype://username:password@server:port/database
## Documentation:
#    http://docs.sqlalchemy.org/en/rel_1_0/core/engines.html
## Examples: 
#    mysql://user:pass@localhost/mydatabase
#    sqlite:///path/to/foo.db
SQLALCHEMY_DATABASE_URI = "sqlite:///database.db"


###  SECURITY  ###
# Used for sessions 
import os
SECRET_KEY = os.urandom(24)


###  EXTERNAL HTML LIBRARIES  ###
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