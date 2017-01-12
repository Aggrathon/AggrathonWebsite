"""
	This module adds an optional image carousel to every page
"""
import app

app.add_hook(app.HOOK_PAGE_MODULE_ABOVE, ("modules/images/carousel.html", add_images_to_data, save_images), 0)

def add_images_to_data(data):
	pass

def save_images(data):
	pass