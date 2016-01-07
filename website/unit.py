import unittest
import timeit
from model import *

def profile_time(func):
    def wrapper(*args, **kwargs):
        beg_ts = timeit.default_timer()
        func(*args, **kwargs)
        end_ts = timeit.default_timer()
        print("Elapsed time in %r: %f" % (str(func), end_ts - beg_ts))
    return wrapper

def setup_db():
	app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///test.db"
	db = SQLAlchemy(app)
	if not check_if_setup():
		reset_db()

class TestProjectModel(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		setup_db()
	
	@profile_time
	def test_create(self):
		path = "a"
		while Project.query.filter_by(path=path).first() is not None:
			path += 'a'
		num = Project.query.count()
		project_set(path, "a", "text", "short", "img", None, ["im", "ag", "es"], ["1", "2"], ["1", "2"], True, flash_result=False)
		self.assertEqual(num+1, Project.query.count(), "Project not created")
	
	@profile_time
	def test_edit(self):
		project_set("a", "a", "text", "short", "img", None, ["im", "ag", "es"], ["1", "2"], ["1", "2"], True, flash_result=False)
		project_set("a", "a", "text", "short", "img", None, ["im", "ag", "es"], ["1", "2"], ["1", "2"], False, flash_result=False)
		project_set("a", "a", "text", "short", "img", None, ["im", "ag", "es"], ["1", "2"], ["1", "2"], True, flash_result=False)
		project_set("a", "a", "text", "short", "img", None, ["ag", "im", "es"], ["1", "2"], ["1", "2"], True, flash_result=False)
		project_set("a", "a", "text", "short", "img", None, [], ["1", "2"], ["1", "2"], True, flash_result=False)
		project_set("a", "a", "text", "short", "img", None, ["im", "ag", "es"], ["1", "2"], ["1", "2"], True, flash_result=False)
		project_set("a", "a", "text", "short", "img", None, ["im", "ag", "es"], ["1", "2"], ["1", "2"], True, flash_result=False)
		project_set("a", "a", "text", "short", "img", None, ["im", "ag", "es"], ["2", "1"], ["1", "2"], True, flash_result=False)
		project_set("a", "a", "text", "short", "img", None, ["im", "ag", "es"], ["2", "1"], ["2", "1"], True, flash_result=False)
		project_set("a", "a", "text", "short", "img", None, ["im", "ag", "es"], ["1", "2"], ["1", "2"], True, flash_result=False)
		project_set("a", "a", "text", "short", "img", None, ["im", "ag", "es"], [], [], True, flash_result=False)
		project_set("a", "a", "text", "short", "img", None, ["im", "ag", "es"], ["1", "2"], ["1", "2"], True, flash_result=False)
		
	@profile_time
	def test_delete(self):
		project_set("a", "a", "text", "short", "img",  None, ["im", "ag", "es"], ["1", "2"], ["1", "2"], True, flash_result=False)
		num = Project.query.count()
		project_delete("a")
		self.assertEqual(num-1, Project.query.count(), "Project not deleted")
	
	@profile_time
	def test_version(self):
		project_set("a", "a", "text", "short", "img", None, [], [], [], True, flash_result=False)
		project_version_set("a", [{'major':0, 'minor':0, 'patch':0, 'changelog':""},{'major':2, 'minor':3, 'patch':0, 'changelog':"asdds 2"},{'major':1, 'minor':4, 'patch':1, 'changelog':"asdds 1"}])
		project_version_set("a", [{'major':0, 'minor':0, 'patch':0, 'changelog':""},{'major':2, 'minor':3, 'patch':0, 'changelog':"asdds 2"},{'major':1, 'minor':4, 'patch':1, 'changelog':"asdds 1 adasdasd"}])
		project_version_set("a", [{'major':0, 'minor':0, 'patch':0, 'changelog':""},{'major':2, 'minor':3, 'patch':0, 'changelog':"asdds 2"}])
		project_version_set("a", [{'major':0, 'minor':0, 'patch':0, 'changelog':""},{'major':2, 'minor':3, 'patch':0, 'changelog':"asdds 2"},{'major':1, 'minor':4, 'patch':1, 'changelog':"asdds 1"}])
		project_version_set("a", [{'major':0, 'minor':0, 'patch':0, 'changelog':""}])
		project_version_set("a", [{'major':0, 'minor':0, 'patch':0, 'changelog':"", 'file_titles':[], 'file_urls':[]}])
		project_version_set("a", [{'major':0, 'minor':0, 'patch':0, 'changelog':"", 'file_titles':['asd'], 'file_urls':['asd']}])
		project_version_set("a", [{'major':0, 'minor':0, 'patch':0, 'changelog':"", 'file_titles':['asd', 'dfg'], 'file_urls':['asd', 'dfg']}])
		project_version_set("a", [{'major':0, 'minor':0, 'patch':0, 'changelog':"", 'file_titles':['asd2', 'dfg'], 'file_urls':['asd2', 'dfg']}])
		project_version_set("a", [{'major':0, 'minor':0, 'patch':0, 'changelog':"", 'file_titles':['asd'], 'file_urls':['asd']}])
		project_version_set("a", [{'major':0, 'minor':0, 'patch':0, 'changelog':"", 'file_titles':[], 'file_urls':[]}])
		project_version_set("a", [{'major':0, 'minor':0, 'patch':0, 'changelog':""}])
		project_version_set("a", [{'major':0, 'minor':0, 'patch':0, 'changelog':"", 'file_titles':['asd2', 'dfg'], 'file_urls':['asd2', 'dfg']},{'major':2, 'minor':3, 'patch':0, 'changelog':"asdds 2"},{'major':1, 'minor':4, 'patch':1, 'changelog':"asdds 1"}])
		numver = ProjectVersion.query.count()
		numfil = ProjectFile.query.count()
		project_delete("a")
		self.assertEqual(numver-3, ProjectVersion.query.count(), "Project versions not deleted")
		self.assertEqual(numfil-2, ProjectFile.query.count(), "Project files not deleted")
	
	#@profile_time
	#def test_set_time(self):
	#	project_set("a", "a", "text", "short", "img", None, ["im", "ag", "es"], ["1", "2"], ["1", "2"], True, flash_result=False)
	#	project_version_set("a", [{'major':0, 'minor':0, 'patch':0, 'changelog':"", 'file_titles':['asd2', 'dfg'], 'file_urls':['asd2', 'dfg']},{'major':2, 'minor':3, 'patch':0, 'changelog':"asdds 2"},{'major':1, 'minor':4, 'patch':1, 'changelog':"asdds 1"}])

if __name__ == '__main__':
	setup_db()
	unittest.main()