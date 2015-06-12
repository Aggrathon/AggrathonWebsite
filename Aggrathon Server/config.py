### Flask Config ###

# DEBUG should not be True on any kind of live server
DEBUG = True



### Database Config ###

# SQLALCHEMY_DATABASE_URI Pattern:
#    servertype://username:password@server:port/database
# Documentation:
#    http://docs.sqlalchemy.org/en/rel_1_0/core/engines.html
# Examples: 
#    mysql://user:pass@localhost/mydatabase
#    sqlite:////absolute/path/to/foo.db
SQLALCHEMY_DATABASE_URI = "sqlite:///database.db"		#