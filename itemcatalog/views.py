from flask import Flask, render_template, request, redirect, url_for, flash, \
	jsonify

from itemcatalog import app
from itemcatalog.login.views import login_blueprint

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime

from models import Base, Category, Item, Users

from flask import session as login_session
import random, string

from forms import CategoryForm, ItemForm

app.register_blueprint(login_blueprint)

engine = create_engine('postgres://ryztryqknsyzog:fVxpW9KcpmHAFAqMo1mBcidICf@ec2-107-21-219-109.compute-1.amazonaws.com:5432/d4kcqmr928j0p2')  # noqa
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


@app.route('/')
@app.route('/category/')
def showCategories():
    categories = session.query(Category).order_by(Category.name)
    items = session.query(Item).order_by(Item.dateCreated).slice(0, 10)
    return render_template('category.html', categories=categories, items=items)


@app.route('/user/<int:users_id>')
def showUser(user_id):
    # Should user profile be invisible? Perhaps. Then no number
    return 'Users will see profiles here.'


@app.route('/category/add', methods=['GET','POST'])
def addCategory():
    if 'username' not in login_session:
        return redirect('/login')
    form = CategoryForm()
    if request.method == 'POST': # and form.validate()
        category = Category()
        category.name = form.name.data
        category.description = form.description.data
        category.picture = form.picture.data
        category.dateCreated = datetime.now()
        category.users_id = login_session['users_id']
        session.add(category)
        session.commit() 
        flash('New Category %s Successfully Created' % category.name)
        return redirect(url_for('showCategories'))
    else:
        return render_template('newCategory.html', form=form)

@app.route('/category/<int:category_id>/')
def showCategory(category_id):
    return "This will show a category."


@app.route('/category/<int:category_id>/edit/', methods=['GET','POST'])
def editCategory(category_id):
    if 'username' not in login_session:
        return redirect('/login')    
    category = session.query(Category).filter_by(id=category_id).one()
    form = CategoryForm(obj=category)
    if request.method == 'POST':  # and form.validate()
        category.name = form.name.data
        category.description = form.description.data
        category.picture = form.picture.data
        session.add(category)
        session.commit()
        flash(' Category %s Successfully Edited' % category.name)
        return redirect(url_for('showCategory', category_id=category_id))
    else:
        return render_template('editCategory.html', form=form, category=category)


@app.route('/category/<int:category_id>/delete/')
def deleteCategory(category_id):
    return 'Delete a category here.'


@app.route('/item/<int:item_id>/')
def showItem(item_id):
    return 'The item page will a particular item.'


@app.route('/category/<int:category_id>/item/add/', methods=['GET','POST'])
def addItem(category_id):
    if 'username' not in login_session:
        return redirect('/login')
    category = session.query(Category).filter_by(id=category_id).one()
    form = ItemForm()
    if request.method == 'POST': # and form.validate()
        item = Item()
        item.name = form.name.data
        item.description = form.description.data
        item.picture = form.picture.data
        item.dateCreated = datetime.now()
        item.users_id = login_session['users_id']
        item.category_id = category_id
        session.add(item)
        session.commit() 
        flash('New Category %s Successfully Created' % category.name)
        return redirect(url_for('showCategories'))
    else:
        return render_template('newItem.html', form=form, category=category)

@app.route('/item/<int:item_id>/edit/', methods=['GET','POST'])
def editItem(item_id):
    if 'username' not in login_session:
        return redirect('/login')    
    item = session.query(Item).filter_by(id=item_id).one()
    form = ItemForm(obj=item)
    if request.method == 'POST':  # and form.validate()
        item.name = form.name.data
        item.description = form.description.data
        item.picture = form.picture.data
        session.add(item)
        session.commit()
        flash(' Item %s Successfully Edited' % item.name)
        return redirect(url_for('showCategory', category_id=item.category_id))
    else:
        return render_template('editItem.html', form=form, item=item)

@app.route('/item/<int:item_id>/delete')
def deleteItem(item_id):
    return 'Delete a item here.'
