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
@app.route('/home/')
def showHome():
    categories = session.query(Category).order_by(Category.name)
    items = session.query(Item).order_by(Item.dateCreated.desc()).slice(0, 10)
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
        return redirect(url_for('showHome'))
    else:
        return render_template('newCategory.html', form=form)

@app.route('/category/<int:category_id>/')
def showCategory(category_id):
    category = session.query(Category).filter_by(id=category_id).one()
    items = session.query(Item).filter_by(category_id=category.id)
    if 'users_id' in login_session and category.users_id == login_session['users_id']:
        editCategory = True
    else:
        editCategory = False
    return render_template('showCategory.html', category=category, 
        items=items, editCategory=editCategory)


@app.route('/category/<int:category_id>/edit/', methods=['GET','POST'])
def editCategory(category_id):
    if 'username' not in login_session:
        return redirect('/login')
    category = session.query(Category).filter_by(id=category_id).one()
    if category.users_id != login_session['users_id']:
        flash(' You are not authorized to make that edit.')
        return redirect(url_for('showCategory', category_id=category_id))
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


@app.route('/category/<int:category_id>/delete/', methods=['GET','POST'])
def deleteCategory(category_id):
    if 'username' not in login_session:
        return redirect('/login')
    category = session.query(Category).filter_by(id=category_id).one()
    if category.users_id != login_session['users_id']:
        flash(' You are not authorized to delete this category.')
        return redirect(url_for('showCategory', category_id=category_id))
    if login_session['users_id'] != category.users_id:
        flash('User does not have permission to delete %s.' % category.name)
        return redirect(url_for('showCategory', category_id = category.id))
    if request.method == 'POST':
        session.delete(category)
        flash('%s Successfully Deleted' % category.name)
        session.commit()
        return redirect(url_for('showHome'))
    else:
        return render_template('deleteCategory.html',category=category)


@app.route('/category/<int:category_id>/item/add/', methods=['GET','POST'])
def addItem(category_id):
    if 'username' not in login_session:
        return redirect('/login')
    category = session.query(Category).filter_by(id=category_id).one()
    if category.users_id != login_session['users_id']:
        flash(' You are not authorized add items to that category.')
        return redirect(url_for('showCategory', category_id=category_id))
    form = ItemForm()
    if request.method == 'POST': # and form.validate()
        item = Item()
        item.name = form.name.data
        item.description = form.description.data
        item.picture = form.picture.data
        item.amazon_asin = form.amazon_asin.data
        item.dateCreated = datetime.now()
        item.users_id = login_session['users_id']
        item.category_id = category_id
        session.add(item)
        session.commit() 
        flash('New Category %s Successfully Created' % category.name)
        return redirect(url_for('showHome'))
    else:
        return render_template('newItem.html', form=form, category=category)


@app.route('/category/<int:category_id>/item/add/list', methods=['GET','POST'])
def areaAddItem(category_id):
    if 'username' not in login_session:
        return redirect('/login')
    category = session.query(Category).filter_by(id=category_id).one()
    if category.users_id != login_session['users_id']:
        flash(' You are not authorized add items to that category.')
        return redirect(url_for('showCategory', category_id=category_id))
    if request.method == 'POST':
        itemslist = request.form['itemslist'].splitlines(True)
        for item in itemslist:
            newItem = Item(
                name=item, 
                dateCreated=datetime.now(), 
                users_id=login_session['users_id'],
                category_id = category_id)
            session.add(newItem)
            session.commit() 
            flash('New Category %s Successfully Created' % category.name)
        return redirect(url_for('showHome'))
    else:
        return render_template('areanewItem.html', category=category)


@app.route('/item/<int:item_id>/edit/', methods=['GET','POST'])
def editItem(item_id):
    if 'username' not in login_session:
        return redirect('/login')    
    item = session.query(Item).filter_by(id=item_id).one()
    if item.users_id != login_session['users_id']:
        flash(' You are not authorized to make that edit.')
        return redirect(url_for('showCategory', category_id=item.category_id))
    form = ItemForm(obj=item)
    if request.method == 'POST':  # and form.validate()
        item.name = form.name.data
        item.description = form.description.data
        item.picture = form.picture.data
        item.amazon_asin = form.amazon_asin.data
        session.add(item)
        session.commit()
        flash(' Item %s Successfully Edited' % item.name)
        return redirect(url_for('showCategory', category_id=item.category_id))
    else:
        return render_template('editItem.html', form=form, item=item)


@app.route('/item/<int:item_id>/delete', methods=['GET','POST'])
def deleteItem(item_id):
    if 'username' not in login_session:
        return redirect('/login')
    item = session.query(Item).filter_by(id=item_id).one()
    if item.users_id != login_session['users_id']:
        flash(' You are not authorized to delete that item.')
        return redirect(url_for('showCategory', category_id=item.category_id))
    category = session.query(Category).filter_by(id=item.category_id).one()
    if login_session['users_id'] != item.users_id:
        flash('User does not have permission to delete %s.' % category.name)
        return redirect(url_for('showCategory', category_id = category.id))
    if request.method == 'POST':
        session.delete(item)
        flash('%s Successfully Deleted' % item.name)
        session.commit()
        return redirect(url_for('showCategory', category_id=category.id))
    else:
        return render_template('deleteItem.html',item=item)
