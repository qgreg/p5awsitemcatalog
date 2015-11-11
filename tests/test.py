from flask import Flask
from flask import session as login_session
from itemcatalog import app
from flask.ext.testing import TestCase

from sqlalchemy.schema import MetaData, DropConstraint
from sqlalchemy.engine import create_engine
from sqlalchemy.orm.session import Session
from sqlalchemy.orm import sessionmaker

from itemcatalog.models import Base, Category, Item, Users  

from flask_wtf.csrf import CsrfProtect


class ItemCatalogTestCase(TestCase):

    def create_app(self):
        app = Flask(__name__)
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        return app


    def test_home(self):
        tester = app.test_client(self)
        response = tester.get('/home/', content_type='html/text')
        self.assert200(response)


class TestRenderTemplates(TestCase):

    def create_app(self):
        app = Flask(__name__)
        return app


    def setUp(self):
        app.config['TESTING'] = True
        global engine, session
        app.secret_key = 'super_secret_key'
        engine = create_engine("postgres://vagrant:vagrant@localhost/testdb")
        Base.metadata.create_all(engine)
        Base.metadata.bind = engine
        DBSession = sessionmaker(bind=engine)
        session = DBSession()
        CsrfProtect(app)
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['WTF_CSRF_CHECK_DEFAULT'] = False


    def tearDown(self):
        session.close()
        engine.dispose()


    def test_add_category_post_simple(self):
        print "Testing ", app.config['TESTING']
        print "CSRF", app.config['WTF_CSRF_ENABLED']
        print "CSRF All Default ", app.config['WTF_CSRF_CHECK_DEFAULT']
        tester = app.test_client(self)
        with tester.session_transaction() as sess:
            sess['username'] = "Test"
            sess['users_id'] = 1
            sess['csrf_token'] = "testplaceholder"
        payload = dict(
            name='Testing',
            description='This is a description.',
            picture='http://www.lessons4living.com/images/penclchk.gif')
        response = tester.post('/category/add', data=payload, follow_redirects=True)
        print response.data
        self.assert200(response)


"""    def test_add_category_post(self):
        # set an user_id
        with app.test_client(self) as c:
            with c.session_transaction() as sess:
                sess['username'] = "Test"
                sess['users_id'] = 1
            # Post valid form data. name description url
            payload = dict(
                name='Testing',
                description='This is a description.',
                picture='http://www.lessons4living.com/images/penclchk.gif')
            response = c.post('/category/add', data=payload, follow_redirects=True)
            print response.data
            category = session.query(Category).filter_by(name="Testing").one()
            self.assertEquals(category.name == "Testing")"""


class TestNotRenderTemplates(TestCase):

    def create_app(self):
        render_templates = False
        app = Flask(__name__)
        return app


    def setUp(self):
        global engine, session
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.secret_key = 'super_secret_key'
        engine = create_engine("postgres://vagrant:vagrant@localhost/testdb")
        Base.metadata.create_all(engine)
        Base.metadata.bind = engine
        DBSession = sessionmaker(bind=engine)
        session = DBSession()


    def tearDown(self):
        session.close()
        engine.dispose()


    def test_home_page_loads(self):
        tester = app.test_client(self)
        response = tester.get('/home/', content_type='html/text')
        self.assertTemplateUsed('category.html')


    def test_add_category_no_username(self):
        tester = app.test_client(self)
        response = tester.get('/category/add', content_type='html/text')
        self.assertRedirects(response, '/login')


    def test_add_category_username_exists(self):
        with app.test_client(self) as c:
            with c.session_transaction() as sess:
                sess['username'] = "Test"
            response = c.get('/category/add', content_type='html/text')
            self.assertTemplateUsed('newCategory.html')


if __name__ == '__main__':
    unittest.main()
