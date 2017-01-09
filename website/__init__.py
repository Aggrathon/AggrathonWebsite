__all__ = ["app", "database", "model", "routes", "view", "modules"]

### List of work left:
#	TODO		[Bugs]		Show Project Dates on project page
#	TODO		[Bugs]		Fix Project Versions
#	TODO		[Meta]		Write readme (and license?)
#	TODO		[Files]		Improve file management
#	OPTIONAL	[Feature]		Backup
#	OPTIONAL	[Feature]		Cache
#	OPTIONAL	[Admin]		Create a sub-setup page with raw access to css and other files

from app import app

if __name__ == '__main__':
	import os
	HOST = os.environ.get('SERVER_HOST', 'localhost')
	try:
		PORT = int(os.environ.get('SERVER_PORT', '5555'))
	except ValueError:
		PORT = 5555
	app.run(HOST, PORT)