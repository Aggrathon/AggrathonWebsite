from flask import Flask
from flask_login import LoginManager
from flask_mail import Mail
from flask_recaptcha import ReCaptcha

app = Flask(__name__)
app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True
app.config.from_pyfile("config.py")

login_manager = LoginManager(app)
mail = Mail(app)
recaptcha = ReCaptcha(app=app)


# Make the WSGI interface available at the top level so wfastcgi can get it.
wsgi_app = app.wsgi_app


#Include all routes
from routes import *

### List of work left todo:
#	TODO		[Meta]		Write readme (and license?)
#	OPTIONAL	[Structure]	Break the big files into modules based on feature
#	OPTIONAL	[Feature]	Backup
#	OPTIONAL	[Feature]	Cache

if __name__ == '__main__':
	import os
	HOST = os.environ.get('SERVER_HOST', 'localhost')
	try:
		PORT = int(os.environ.get('SERVER_PORT', '5555'))
	except ValueError:
		PORT = 5555
	import database
	if not database.check_if_setup():
		if app.config['DATABASE_SCHEMA_ERROR_ACTION'] == 'NOTHING':
			print('\033[93m'+"The Database Schema doesn't match the website, check the database or use the 'Reset Database' function (in /admin/setup/) to remove old data"+'\033[0m')
		else:
			database.reset_db()
			print('\033[93m'+"The Database has been reset due to not matching the website"+'\033[0m')
	os.makedirs(os.path.join('files','projects'), exist_ok=True)
	app.run(HOST, PORT)