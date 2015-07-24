### Flask Config ###

# DEBUG should not be True on any kind of live server
DEBUG = True


# Used for sessions
SECRET_KEY = 'development key'


### External Libraries ###
#Bootstrap: parent directory, JQuery: actual script
#Online
#BOOTSTRAP = 'https://maxcdn.bootstrapcdn.com/bootstrap/3.3.5/'
#JQUERY = 'https://ajax.googleapis.com/ajax/libs/jquery/1.11.3/jquery.min.js'
#Offline
BOOTSTRAP = '/static/offline/bootstrap-3.3.5/'
JQUERY = '/static/offline/jquery-1.11.3.min.js'

### Database Config ###

# SQLALCHEMY_DATABASE_URI Pattern:
#    servertype://username:password@server:port/database
# Documentation:
#    http://docs.sqlalchemy.org/en/rel_1_0/core/engines.html
# Examples: 
#    mysql://user:pass@localhost/mydatabase
#    sqlite:////absolute/path/to/foo.db
SQLALCHEMY_DATABASE_URI = "sqlite:///database.db"