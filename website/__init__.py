__all__ = ["app", "database", "model", "routes", "view", "modules"]

### List of work left:
#	TODO	[Projects]	Change projects to using pages
#	TODO	[Pages]		Create modules for pages
#	TODO	[Bugs]		Show Project Dates on project page
#	TODO	[Bugs]		Fix Project Versions
#	TODO	[Meta]		Write readme (and license?)
#	TODO	[Files]		Improve file management
#	OPT		[Feature]	Backup
#	OPT		[Feature]	Cache
#	OPT		[Admin]		Create a sub-setup page with raw access to css and other files

from app import app

if __name__ == '__main__':
	import os
	HOST = os.environ.get('SERVER_HOST', 'localhost')
	try:
		PORT = int(os.environ.get('SERVER_PORT', '5555'))
	except ValueError:
		PORT = 5555
	app.run(HOST, PORT)