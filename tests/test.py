from flask import Flask, current_app
from flask import session as login_session
from flask.ext.testing import TestCase
from flask.ext.sqlalchemy import SQLAlchemy
import random, string

from itemcatalog.category.models import db, Category, Item, Users  

from flask_wtf.csrf import CsrfProtect, generate_csrf

#from selenium import webdriver
#from selenium.webdriver.common.keys import Keys

def CreateTUser():
    if Users.query.filter_by(name='Test').first() == None:
        newUser = Users('Test', 'test@test.com', '', False)
        db.session.add(newUser)
        db.session.commit()

def ClearCategory():
    while Category.query.filter_by(name='Test').first() != None:
        category = Category.query.filter_by(name='Test').first()
        db.session.delete(category)
    db.session.commit()

class ItemCatalogTestCase(TestCase):

    def create_app(self):
        app = Flask(__name__)
        app.config.from_pyfile('testconfig.py')
        db.init_app(app)
        from itemcatalog.login.views import login_blueprint
        app.register_blueprint(login_blueprint)
        from itemcatalog.category.views import category
        app.register_blueprint(category)
        with app.app_context():
            db.create_all()
        return app

    def setUp(self):
        app = current_app._get_current_object()
        self.tester = app.test_client()

    def test_home(self):
        with self.app.test_client() as tester:
            response = tester.get('/home/', content_type='html/text')
            self.assert200(response)


class TestRenderTemplates(TestCase):


    def create_app(self):
        app = Flask(__name__)
        app.config.from_pyfile('testconfig.py')
        db.init_app(app)
        from itemcatalog.login.views import login_blueprint
        app.register_blueprint(login_blueprint)
        from itemcatalog.category.views import category
        app.register_blueprint(category)
        with app.app_context():
            db.create_all()
        CsrfProtect(app)
        return app


    def setUp(self):
        app = current_app._get_current_object()
        self.tester = app.test_client()
        app.config['WTF_CSRF_METHODS'] = ""
        app.config['WTF_CSRF_ENABLED'] = False


    def tearDown(self):
        db.session.close()


    def test_show_category(self):
        with self.app.test_client() as tester:
            response = tester.get('/category/Test', content_type='html/text')
            print response.data
            self.assertTemplateUsed('showCategory.html') 


    def test_add_category_post_simple(self):
        with self.app.test_client() as tester:
            CreateTUser()
            ClearCategory()
            users = Users.query.filter_by(name='Test').first_or_404()
            testname = "Test"
            testname += str(''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(8)))
            with tester.session_transaction() as sess:
                sess['username'] = "Test"
                sess['users_id'] = users.id
            payload = dict(
                name=testname,
                description='This is a description.',
                picture='http://www.lessons4living.com/images/penclchk.gif')
            response = tester.post('/category/add', data=payload, follow_redirects=True)
            self.assert200(response)
            self.assertTrue(testname in response.data)
            category = Category.query.filter_by(name=testname).first_or_404()
            db.session.delete(category)
            db.session.commit()
            db.session.delete(users)
            db.session.commit()

"""
class TestWithUserandCategorySelenium(TestCase):

    def create_app(self):
        app = Flask(__name__)
        app.config.from_pyfile('testconfig.py')
        db.init_app(app)
        from itemcatalog.login.views import login_blueprint
        app.register_blueprint(login_blueprint)
        from itemcatalog.category.views import category
        app.register_blueprint(category)
        with app.app_context():
            db.create_all()
        return app


    def setUp(self):
        app = current_app._get_current_object()
        self.tester = app.test_client()
        self.driver = webdriver.Firefox(executable_path='/Application/')
        with self.app.test_client() as tester:
            CreateTUser()
            ClearCategory()
            user = Users.query.filter_by(name='Test').first_or_404()
            newCategory = Category('Test', '', '', user.id)
            db.session.add(newCategory)
            db.session.commit()


    def test_show_category_with_id(self):
        driver = self.driver
        with self.app.test_client() as tester:
            category = Category.query.filter_by(name='Test').first_or_404()
            urlid = '/category/id/' + str(category.id)
            driver.get(urlid)
            assert "Category: Test" in driver.page_source 


    def tearDown(self):
        with self.app.test_client() as tester:
            users = Users.query.all()
            ClearCategory()
            while Users.query.first() != None:
                user = Users.query.first()
                db.session.delete(user)
            db.session.commit()
            db.session.close()
            self.driver.close()
"""

class TestNoRenderTemplates(TestCase):

    def create_app(self):
        app = Flask(__name__)
        app.config.from_pyfile('testconfig.py')
        db.init_app(app)
        from itemcatalog.login.views import login_blueprint
        app.register_blueprint(login_blueprint)
        from itemcatalog.category.views import category
        app.register_blueprint(category)
        with app.app_context():
            db.create_all()
        return app


    def setUp(self):
        app = current_app._get_current_object()
        self.tester = app.test_client()
        render_templates = False
 

    def tearDown(self):
        db.session.close()


    def test_home_page_loads(self):
        with self.app.test_client() as tester:
            response = tester.get('/home/', content_type='html/text')
            self.assertTemplateUsed('category.html')


    def test_add_category_no_username(self):
        with self.app.test_client() as tester:
            response = tester.get('/category/add', content_type='html/text')
            self.assertRedirects(response, '/login')


    def test_add_category_username_exists(self):
        with self.app.test_client() as tester:
            with tester.session_transaction() as sess:
                sess['username'] = "Test"
            response = tester.get('/category/add', content_type='html/text')
            print response
            self.assertTemplateUsed('newCategory.html')


if __name__ == '__main__':
    unittest.main()
