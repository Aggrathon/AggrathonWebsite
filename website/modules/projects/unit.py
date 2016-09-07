import unittest
import timeit
import app
from modules.projects.model import *
from database import reset_db

def profile_time(func):
    def wrapper(*args, **kwargs):
        beg_ts = timeit.default_timer()
        func(*args, **kwargs)
        end_ts = timeit.default_timer()
        print("Elapsed time in %r: %f" % (str(func), end_ts - beg_ts))
    return wrapper

def setup():
	app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///:memory:"
	app.config['DATABASE_SCHEMA_ERROR_ACTION'] = 'RESET'
	db = SQLAlchemy(app)
	reset_db()

class TestProjectModel(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		setup()
	
	@profile_time
	def test_projects_create(self):
		path = "a"
		while Project.query.filter_by(path=path).first() is not None:
			path += 'a'
		num = Project.query.count()
		project_set(path, "a", "text", "short", "img", None, ["im", "ag", "es"], ["1", "2"], ["1", "2"], True, flash_result=False)
		db.session.expire_all()
		self.assertEqual(num+1, Project.query.count(), "Project not created")
	
	@profile_time
	def test_projects_edit(self):
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
		
	@profile_time
	def test_projects_delete(self):
		project_set("a", "a", "text", "short", "img",  None, ["im", "ag", "es"], ["1", "2"], ["1", "2"], True, flash_result=False)
		num = Project.query.count()
		num_img = ProjectImage.query.count()
		num_lnk = ProjectLink.query.count()
		num_feat = ProjectFeatured.query.count()
		num_last = ProjectLast.query.count();
		project_delete("a")
		db.session.expire_all()
		self.assertEqual(num-1, Project.query.count(), "Project not deleted")
		self.assertEqual(num_img-3, ProjectImage.query.count(), "Project images not deleted")
		self.assertEqual(num_lnk-2, ProjectLink.query.count(), "Project links not deleted")
		self.assertEqual(num_feat-1, ProjectFeatured.query.count(), "Project not removed from featured")
		self.assertEqual(num_last-1, ProjectLast.query.count(), "Project not removed from latest")
	
	@profile_time
	def test_projects_version(self):
		project_set("a", "a", "text", "short", "img", None, [], [], [], True, flash_result=False)
		project_versions_set("a", [{'major':0, 'minor':0, 'patch':0, 'changelog':"", 'date':'2016-01-01'},{'major':2, 'minor':3, 'patch':0, 'changelog':"asdds 2", 'date':'2016-01-01'},{'major':1, 'minor':4, 'patch':1, 'changelog':"asdds 1", 'date':'2016-01-01'}])
		project_versions_set("a", [{'major':0, 'minor':0, 'patch':0, 'changelog':"", 'date':'2016-01-01'},{'major':2, 'minor':3, 'patch':0, 'changelog':"asdds 2", 'date':'2016-01-01'},{'major':1, 'minor':4, 'patch':1, 'changelog':"asdds 1 adasdasd", 'date':'2016-01-01'}])
		project_versions_set("a", [{'major':0, 'minor':0, 'patch':0, 'changelog':"", 'date':'2016-01-01'},{'major':2, 'minor':3, 'patch':0, 'changelog':"asdds 2", 'date':'2016-01-01'}])
		project_versions_set("a", [{'major':0, 'minor':0, 'patch':0, 'changelog':"", 'date':'2016-01-01'},{'major':2, 'minor':3, 'patch':0, 'changelog':"asdds 2", 'date':'2016-01-01'},{'major':1, 'minor':4, 'patch':1, 'changelog':"asdds 1", 'date':'2016-01-01'}])
		project_versions_set("a", [{'major':0, 'minor':0, 'patch':0, 'changelog':"", 'date':'2016-01-01'}])
		project_versions_set("a", [{'major':0, 'minor':0, 'patch':0, 'changelog':"", 'date':'2016-01-01', 'file_titles':[], 'file_urls':[]}])
		project_versions_set("a", [{'major':0, 'minor':0, 'patch':0, 'changelog':"", 'date':'2016-01-01', 'file_titles':['asd'], 'file_urls':['asd']}])
		project_versions_set("a", [{'major':0, 'minor':0, 'patch':0, 'changelog':"", 'date':'2016-01-01', 'file_titles':['asd', 'dfg'], 'file_urls':['asd', 'dfg']}])
		project_versions_set("a", [{'major':0, 'minor':0, 'patch':0, 'changelog':"", 'date':'2016-01-01', 'file_titles':['asd2', 'dfg'], 'file_urls':['asd2', 'dfg']}])
		project_versions_set("a", [{'major':0, 'minor':0, 'patch':0, 'changelog':"", 'date':'2016-01-01', 'file_titles':['asd'], 'file_urls':['asd']}])
		project_versions_set("a", [{'major':0, 'minor':0, 'patch':0, 'changelog':"", 'date':'2016-01-01', 'file_titles':[], 'file_urls':[]}])
		project_versions_set("a", [{'major':0, 'minor':0, 'patch':0, 'changelog':"", 'date':'2016-01-01'}])
		project_versions_set("a", [{'major':0, 'minor':0, 'patch':0, 'changelog':"", 'date':'2016-01-01', 'file_titles':['asd2', 'dfg'], 'file_urls':['asd2', 'dfg']},{'major':2, 'minor':3, 'patch':0, 'changelog':"asdds 2", 'date':'2016-01-01'},{'major':1, 'minor':4, 'patch':1, 'changelog':"asdds 1", 'date':'2016-01-01'}])
		project_versions_set("a", [{'major':0, 'minor':0, 'patch':0, 'changelog':"", 'date':'2016-02-03', 'file_titles':['asd2', 'dfg'], 'file_urls':['asd2', 'dfg']},{'major':2, 'minor':3, 'patch':0, 'changelog':"asdds 2", 'date':'2016-01-01'},{'major':1, 'minor':4, 'patch':1, 'changelog':"asdds 1", 'date':'2017-01-01'}])
		numver = ProjectVersion.query.count()
		project_version_delete("a", 2, 3, 0)
		numfil = ProjectFile.query.count()
		db.session.expire_all()
		self.assertEqual(numver-1, ProjectVersion.query.count(), "Project version not deleted")
		project_version_set("a", 2, 3, 0,  "asd", '2016-01-01', ["asd"], ["asd"],flash_result=False)
		db.session.expire_all()
		self.assertEqual(numver, ProjectVersion.query.count(), "Project version not created")
		self.assertEqual(numfil+1, ProjectFile.query.count(), "Project version files not created")
		project_version_set("a", 2, 3, 0,  "asd", '2016-01-01', ["asd", "asd2"], ["asd", "asd2"],flash_result=False)
		db.session.expire_all()
		self.assertEqual(numfil+2, ProjectFile.query.count(), "Project version not updated")
		project_delete("a")
		db.session.expire_all()
		self.assertEqual(numver-3, ProjectVersion.query.count(), "Project versions not deleted")
		self.assertEqual(numfil-2, ProjectFile.query.count(), "Project files not deleted")
	
	def test_projects_tags(self):
		numTags = ProjectTag.query.filter(ProjectTag.tag.isnot("test")).filter(ProjectTag.tag.isnot("test2")).count()
		project_set("a", "a", "text", "short", "img", None, [], [], [], True, flash_result=False)
		project_set("a", "a", "text", "short", "img", "test", [], [], [], True, flash_result=False)
		project_set("a", "a", "text", "short", "img", "test, test2", [], [], [], True, flash_result=False)
		project_set("a", "a", "text", "short", "img", None, [], [], [], True, flash_result=False)
		project_set("a", "a", "text", "short", "img", "test, test", [], [], [], True, flash_result=False)
		db.session.expire_all()
		self.assertEqual(numTags+2, ProjectTag.query.count(), "Tags not created inline")
		project_tags_create("test3")
		db.session.expire_all()
		self.assertEqual(numTags+3, ProjectTag.query.count(), "Tag not created standalone")
		project_tags_delete("test")
		project_tags_delete("test2")
		project_tags_delete("test3")
		db.session.expire_all()
		self.assertFalse(Project.query.filter_by(path="a").first().tags, "Tag not removed")
		self.assertEqual(numTags, ProjectTag.query.count(), "Tags not deleted (%s)"%ProjectTag.query.all())

	def test_projects_list(self):
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

	def test_projects_latest(self):
		project_set("a", "a", "text", "short", "img", None, [], [], [], True, flash_result=False)
		project_set("a2", "a", "text", "short", "img", None, [], [], [], True, flash_result=False)
		pid = ProjectLast.query.order_by(ProjectLast.time.desc()).first().project_id
		db.session.expire_all()
		self.assertEqual(Project.query.get(pid).path, "a2", "Project Last not updating when creating Project")
		project_get_admin("a")
		pid = ProjectLast.query.order_by(ProjectLast.time.desc()).first().project_id
		db.session.expire_all()
		self.assertEqual(Project.query.get(pid).path, "a", "Project Last not updating when viewing Project (through edit)")

	def test_projects_featured(self):
		project_set("a", "a", "text", "short", "img", None, [], [], [], True, flash_result=False)
		pid = Project.query.filter_by(path="a").first().id
		db.session.expire_all()
		self.assertIsNotNone(ProjectFeatured.query.get(pid), "Project not set featured when created")
		project_feature_set("a", False)
		db.session.expire_all()
		self.assertIsNone(ProjectFeatured.query.get(pid), "Project not set unfeatured with method")
		project_feature_set("a", True)
		db.session.expire_all()
		self.assertIsNotNone(ProjectFeatured.query.get(pid), "Project not set featured with method")
		project_feature_set("a", True, 5)
		db.session.expire_all()
		self.assertEqual(ProjectFeatured.query.get(pid).priority, 5, "Project featured priority not set with method")

if __name__ == '__main__':
	setup()
	unittest.main()