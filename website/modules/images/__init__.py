"""
	This module adds an optional image carousel to every page
"""
import app
from modules.images import model

app.add_hook(app.HOOK_DATABASE_SETUP_CHECK, model.setup)
app.add_hook(app.HOOK_PAGE_MODULE_ABOVE, (
	"modules/images/carousel.html", model.add_images_to_data, 
	"modules/images/admin.html", model.save_images), 0)
