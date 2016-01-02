import unittest
from model import *

def setup_db():
	app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///test.db"
	db = SQLAlchemy(app)

class TestProjectModel(unittest.TestCase):
	def test_create(self):
		project_set("a", "a", "text", "short", "img", ["im", "ag", "es"], ["1", "2"], ["1", "2"], True, flash_result=False)
		self.assertIsNotNone(Project.query.first(), "Project not created")
	
	def test_edit(self):
		project_set("a", "a", "text", "short", "img", ["im", "ag", "es"], ["1", "2"], ["1", "2"], True, flash_result=False)
		project_set("a", "a", "text", "short", "img", ["im", "ag", "es"], ["1", "2"], ["1", "2"], False, flash_result=False)
		project_set("a", "a", "text", "short", "img", ["im", "ag", "es"], ["1", "2"], ["1", "2"], True, flash_result=False)
		project_set("a", "a", "text", "short", "img", ["ag", "im", "es"], ["1", "2"], ["1", "2"], True, flash_result=False)
		project_set("a", "a", "text", "short", "img", [], ["1", "2"], ["1", "2"], True, flash_result=False)
		project_set("a", "a", "text", "short", "img", ["im", "ag", "es"], ["1", "2"], ["1", "2"], True, flash_result=False)
		project_set("a", "a", "text", "short", "img", ["im", "ag", "es"], ["1", "2"], ["1", "2"], True, flash_result=False)
		project_set("a", "a", "text", "short", "img", ["im", "ag", "es"], ["2", "1"], ["1", "2"], True, flash_result=False)
		project_set("a", "a", "text", "short", "img", ["im", "ag", "es"], ["2", "1"], ["2", "1"], True, flash_result=False)
		project_set("a", "a", "text", "short", "img", ["im", "ag", "es"], ["1", "2"], ["1", "2"], True, flash_result=False)
		project_set("a", "a", "text", "short", "img", ["im", "ag", "es"], [], [], True, flash_result=False)
		project_set("a", "a", "text", "short", "img", ["im", "ag", "es"], ["1", "2"], ["1", "2"], True, flash_result=False)
		
	def test_delete(self):
		project_set("a", "a", "text", "short", "img", ["im", "ag", "es"], ["1", "2"], ["1", "2"], True, flash_result=False)
		num = Project.query.count()
		project_delete("a")
		self.assertEqual(num-1, Project.query.count(), "Project not deleted")

if __name__ == '__main__':
	setup_db()
	reset_db()
	unittest.main()