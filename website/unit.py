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
	
	#@profile_time
	def test_create(self):
		path = "a"
		while Project.query.filter_by(path=path).first() is not None:
			path += 'a'
		num = Project.query.count()
		project_set(path, "a", "text", "short", "img", None, ["im", "ag", "es"], ["1", "2"], ["1", "2"], True, flash_result=False)
		self.assertEqual(num+1, Project.query.count(), "Project not created")
	
	#@profile_time
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
		project_set("a1", "a", "text", "short", "img", None, ["im", "ag", "es"], ["1", "2"], ["1", "2"], True, flash_result=False)
		#latest assignment moved to view instead of edit: self.assertEqual(Project.query.filter_by(path="a1").first().id,ProjectLast.query.order_by(ProjectLast.time.desc()).first().project_id, "Latest edited page not updated")
		project_move("a", "a2")
		project_move("a1", "a2")
		project_move("a2", "a1")
		project_move("a2", "a")
		project_move("a3", "a4")
		
	#@profile_time
	def test_delete(self):
		project_set("a", "a", "text", "short", "img",  None, ["im", "ag", "es"], ["1", "2"], ["1", "2"], True, flash_result=False)
		num = Project.query.count()
		project_delete("a")
		self.assertEqual(num-1, Project.query.count(), "Project not deleted")
	
	#@profile_time
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
	
	def test_tags(self):
		numTags = ProjectTag.query.filter(ProjectTag.tag.isnot("test")).filter(ProjectTag.tag.isnot("test2")).count()
		project_set("a", "a", "text", "short", "img", None, [], [], [], True, flash_result=False)
		project_set("a", "a", "text", "short", "img", "test", [], [], [], True, flash_result=False)
		project_set("a", "a", "text", "short", "img", "test, test2", [], [], [], True, flash_result=False)
		project_set("a", "a", "text", "short", "img", None, [], [], [], True, flash_result=False)
		project_set("a", "a", "text", "short", "img", "test, test", [], [], [], True, flash_result=False)
		self.assertEqual(numTags+2, ProjectTag.query.count(), "Tags not created inline")
		project_tags_create("test3")
		self.assertEqual(numTags+3, ProjectTag.query.count(), "Tag not created standalone")
		project_tags_delete("test")
		project_tags_delete("test2")
		project_tags_delete("test3")
		self.assertFalse(Project.query.filter_by(path="a").first().tags, "Tag not removed")
		self.assertEqual(numTags, ProjectTag.query.count(), "Tags not deleted (%s)"%ProjectTag.query.all())

	def test_list(self):
		project_set("a", "a", "text", "short", "img", "test,test2,asd", ["im", "ag", "es"], ["1", "2"], ["1", "2"], True, flash_result=False)
		project_list(None, None)
		project_list(None, "created")
		project_list(None, "asd")
		project_list(None, "updated")
		project_list([], None)
		project_list(["asd","test","test2"], None)
		project_list(["dfkhjsjkflhasdjkflhdsafyehaklhbnjklaeyhu"], None)
		project_tags()
		project_list_admin()

if __name__ == '__main__':
	setup_db()
	unittest.main()