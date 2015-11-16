
from flask import Flask, render_template, request, redirect, url_for, flash, \
	jsonify, Blueprint, current_app
from flask.ext.sqlalchemy import SQLAlchemy
from flask import session as login_session 

from models import db, Category, Item, Users

import random, string

from forms import CategoryForm, ItemForm
import re

category = Blueprint(
    'category', __name__,
    template_folder="templates")

@category.route('/')
@category.route('/home/')
def showHome():
    categories = Category.query.order_by(Category.name)
    items = Item.query.order_by(Item.dateCreated.desc()).slice(0, 10)
    return render_template('category.html', categories=categories, items=items)


@category.route('/user/<int:users_id>')
def showUser(user_id):
    # Should user profile be invisible? Perhaps. Then no number
    return 'Users will see profiles here.'


@category.route('/category/add', methods=['GET','POST'])
def addCategory():
    if 'username' not in login_session:
        return redirect('/login')
    form = CategoryForm()
    if form.validate_on_submit():
        category = Category(form.name.data, form.description.data, 
            form.picture.data, login_session['users_id'])
        db.session.add(category)
        db.session.commit()
        flash('New Category %s Successfully Created' % category.name)
        current_app.logger.info('New Category %s Created on %s' % (category.name, str(category.dateCreated)))
        return redirect(url_for('category.showHome'))
    else:
        return render_template('newCategory.html', form=form)


@category.route('/category/id/<int:category_id>/')
def showIdCategory(category_id):
    category = Category.query.filter_by(id=category_id).first_or_404()
    return redirect(url_for('category.showCategory', name=category.name))


@category.route('/category/<name>/')
def showCategory(name):
    category = Category.query.filter_by(name=name).first_or_404()
    items = Item.query.filter_by(category_id=category.id).order_by(Item.name)
    if 'users_id' in login_session and category.users_id == login_session['users_id']:
        editCategory = True
    else:
        editCategory = False
    return render_template('showCategory.html', category=category, 
        items=items, editCategory=editCategory)


@category.route('/category/<name>/edit/', methods=['GET','POST'])
def editCategory(name):
    if 'username' not in login_session:
        return redirect('/login')
    category = Category.query.filter_by(name=name).first_or_404()
    if category.users_id != login_session['users_id']:
        flash(' You are not authorized to make that edit.')
        return redirect(url_for('category.showCategory', category_id=category_id))
    form = CategoryForm(obj=category)
    if form.validate_on_submit():
        category.name = form.name.data
        category.description = form.description.data
        category.picture = form.picture.data
        db.session.add(category)
        db.session.commit()
        flash(' Category %s Successfully Edited' % category.name)
        return redirect(url_for('category.showCategory', name=category.name))
    else:
        return render_template('editCategory.html', form=form, category=category)


@category.route('/category/<name>/delete/', methods=['GET','POST'])
def deleteCategory(name):
    if 'username' not in login_session:
        return redirect('/login')
    category = Category.query.filter_by(name=name).first_or_404()
    if category.users_id != login_session['users_id']:
        flash(' You are not authorized to delete this category.')
        return redirect(url_for('category.showCategory', category_id=category_id))
    if login_session['users_id'] != category.users_id:
        flash('User does not have permission to delete %s.' % category.name)
        return redirect(url_for('category.showCategory', name=category.name))
    if request.method == 'POST':
        db.session.delete(category)
        flash('%s Successfully Deleted' % category.name)
        db.session.commit()
        return redirect(url_for('category.showHome'))
    else:
        return render_template('deleteCategory.html', category=category)


@category.route('/category/<name>/item/add/', methods=['GET','POST'])
def addItem(name):
    if 'username' not in login_session:
        return redirect('/login')
    category = Category.query.filter_by(name=name).first_or_404()
    if category.users_id != login_session['users_id']:
        flash(' You are not authorized add items to that category.')
        return redirect(url_for('category.showCategory', name=name))
    form = ItemForm()
    if form.validate_on_submit():
        item = Item(form.name.data, form.description.data,form.amazon_asin.data,
            form.picture.data, category.id, login_session['users_id'])
        if form.amazon_url.data is not None:
            asin = re.search("[A-Z0-9]{10}", form.amazon_url.data)
            if asin:
                item.amazon_asin = asin.group(0)
        db.session.add(item)
        db.session.commit() 
        flash('New Item %s Successfully Created' % item.name)
        current_app.logger.info('New Category %s Created on %s' % (item.name, 
            str(item.dateCreated)))
        return redirect(url_for('category.showHome'))
    else:
        return render_template('newItem.html', form=form, category=category)


@category.route('/category/<name>/item/add/list', methods=['GET','POST'])
def areaAddItem(name):
    if 'username' not in login_session:
        return redirect('/login')
    category = Category.query.filter_by(id=category_id).first_or_404()
    if category.users_id != login_session['users_id']:
        flash(' You are not authorized add items to that category.')
        return redirect(url_for('category.showCategory', category_id=category_id))
    if request.method == 'POST':
        itemslist = request.form['itemslist'].splitlines(True)
        for item in itemslist:
            newItem = Item(item, "", "", category_id, login_session['users_id'])
            db.session.add(newItem)
            db.session.commit() 
            flash('New Category %s Successfully Created' % category.name)
        return redirect(url_for('category.showHome'))
    else:
        return render_template('areanewItem.html', category=category)


@category.route('/item/<name>/edit/', methods=['GET','POST'])
def editItem(name):
    if 'username' not in login_session:
        return redirect('/login')    
    item = Item.query.filter_by(name=name).first_or_404()
    if item.users_id != login_session['users_id']:
        flash(' You are not authorized to make that edit.')
        category = session.query(Category).filter_by(id=item.category_id)
        return redirect(url_for('category.showCategory', name=category.name))
    form = ItemForm(obj=item)
    if form.validate_on_submit():
        item.name = form.name.data
        item.description = form.description.data
        item.picture = form.picture.data
        if form.amazon_url.data is not None:
            asin = re.search("[A-Z0-9]{10}", form.amazon_url.data)
            if asin:
                item.amazon_asin = asin.group(0)
            else:
                item.amazon_asin = form.amazon_asin.data
        db.session.add(item)
        db.session.commit()
        flash(' Item %s Successfully Edited' % item.name)
        category = Category.query.filter_by(id=item.category_id).first_or_404()
        return redirect(url_for('category.showCategory', name=category.name))
    else:
        return render_template('editItem.html', form=form, item=item)


@category.route('/item/<name>/delete', methods=['GET','POST'])
def deleteItem(name):
    if 'username' not in login_session:
        return redirect('/login')
    item = Item.query.filter_by(name=name).first_or_404()
    if item.users_id != login_session['users_id']:
        flash(' You are not authorized to delete that item.')
        return redirect(url_for('category.showCategory', category_id=item.category_id))
    category = Category.query.filter_by(id=item.category_id).first_or_404()
    if login_session['users_id'] != item.users_id:
        flash('User does not have permission to delete %s.' % category.name)
        return redirect(url_for('category.showCategory', name=category.name))
    if request.method == 'POST':
        db.session.delete(item)
        category = Category.query.filter_by(id=item.category_id).first_or_404()
        flash('%s Successfully Deleted' % item.name)
        db.session.commit()
        return redirect(url_for('category.showCategory', name=category.name))
    else:
        return render_template('deleteItem.html', item=item)


@category.route('/category/JSON')
def categoriesJSON():
    categories = Category.query.all()
    return jsonify(CAtegory=[i.serialize for i in categories])


@category.route('/category/<name>/JSON')
def categoryJSON(name):
    category = Category.query.filter_by(name=name).first_or_404()
    items = Item.query.filter_by(
        category_id=category.id).first_or_404()
    return jsonify(Item=[i.serialize for i in items])


@category.route('/category/<categoryname>/item/<itemname>/JSON')
def restaurantMenuItemJSON(categoryname, itenname):
    item = Item.query(Item).filter_by(
        name=itemname).one()
    return jsonify(Item=[item.serialize])
