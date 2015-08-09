### Flask Config ###

# DEBUG should not be True on any kind of live server
DEBUG = True


# Used for sessions
SECRET_KEY = 'development key'


### External Libraries ###
## Bootstrap: parent directory, JQuery: actual script, Editor: actual js, Editor Config: config and init (TEXTAREA_ID is the selector for the replaced textarea)
## Online
#BOOTSTRAP = 'https://maxcdn.bootstrapcdn.com/bootstrap/3.3.5/'
#JQUERY = 'https://ajax.googleapis.com/ajax/libs/jquery/1.11.3/jquery.min.js'
#EDITOR = '//cdn.ckeditor.com/4.5.1/standard/ckeditor.js'
## Local
BOOTSTRAP = '/static/external/bootstrap-3.3.5/'
JQUERY = '/static/external/jquery-1.11.3.min.js'
EDITOR = '/static/external/CKEditor/custom-4.5.1/ckeditor.js'
EDITOR_CONFIG = """CKEDITOR.replace('TEXTAREA_ID', { customConfig: '/static/external/CKEditor/config/config.js' }); CKEDITOR.dtd.$removeEmpty['span'] = false;"""
EDITOR_JS_INSERT = "CKEDITOR.instances['TEXTAREA_ID'].insertHtml(INSERT_HTML);"

### Database Config ###
## SQLALCHEMY_DATABASE_URI Pattern:
#    servertype://username:password@server:port/database
## Documentation:
#    http://docs.sqlalchemy.org/en/rel_1_0/core/engines.html
## Examples: 
#    mysql://user:pass@localhost/mydatabase
#    sqlite:////absolute/path/to/foo.db
SQLALCHEMY_DATABASE_URI = "sqlite:///database.db"