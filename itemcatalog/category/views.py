
from flask import Flask, render_template, request, redirect, url_for, flash, \
	jsonify, Blueprint, current_app
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.exc import DatabaseError
from flask import session as login_session 

from models import db, Category, Item, Users

import random, string

from forms import CategoryForm, ItemForm
import re

category = Blueprint('category', __name__, template_folder="templates")


@category.route('/')
@category.route('/home/')
def showHome():
    categories = Category.query.order_by(Category.name)
    items = Item.query.order_by(Item.dateCreated.desc()).slice(0, 10)
    return render_template('category.html', categories=categories, items=items)


@category.route('/user/<int:users_id>')
def showUser(users_id):
    if 'username' not in login_session:
        return redirect('/login')
    else:
        adminuser = Users.query.filter_by(id=login_session['users_id']).first_or_404()
        showuser = Users.query.filter_by(id=users_id).first_or_404()
        if adminuser.admin:
            editUser = True
            userslist = Users.query.all()
        else:
            editUser = False
            userslist = None
        categories = Category.query.filter_by(users_id=showuser.id).order_by(category.name)
        return render_template('user.html', user=showuser, categories=categories, editUser=editUser, userslist=userslist)


@category.route('/user/<int:users_id>/change', methods=['POST'])
def changeAdmin(users_id):
    user = Users.query.filter_by(id=users_id).first_or_404()
    if not user.admin:
        flash(' You are not authorized to set admin role.')
        return redirect(url_for('category.showHome'))
    if request.method == 'POST':
        user.admin = request.form['admin']
        db.session.add(user)
        db.session.commit()
        if user.admin:
            flash('%s role changed to admin.', user.name)
        else:
            flash('%s admin role revoked.', user.name)
        db.session.commit()
        return redirect(url_for('category.showHome'))


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
    #items = db.session.query(Item, Category).filter(Item.category_id = Category.id).\
    #    filter_by(category_id=category.id).order_by(Item.name).all()
    items = Item.query.filter_by(category_id=category.id).order_by(Item.name).all()
    editCategory = False
    if 'users_id' in login_session:
        user = Users.query.filter_by(id=login_session['users_id']).first_or_404()
        if category.users_id == login_session['users_id'] or user.admin:
            editCategory = True
    return render_template('showCategory.html', category=category, 
            items=items, editCategory=editCategory)


@category.route('/category/<name>/edit/', methods=['GET','POST'])
def editCategory(name):
    if 'username' not in login_session:
        return redirect('/login')
    else:
        category = Category.query.filter_by(name=name).first_or_404()
        user = Users.query.filter_by(id=login_session['users_id']).first_or_404()
        if category.users_id != login_session['users_id'] and not user.admin:
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
    else:
        category = Category.query.filter_by(name=name).first_or_404()
        user = Users.query.filter_by(id=login_session['users_id'])
        if category.users_id != login_session['users_id'] and not user.admin:
            flash(' You are not authorized to delete this category.')
            return redirect(url_for('category.showCategory', category_id=category_id))
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
    else:
        category = Category.query.filter_by(name=name).first_or_404()
        user = Users.query.filter_by(id=login_session['users_id'])
        if category.users_id != login_session['users_id'] and not user.admin:
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
    else:
        category = Category.query.filter_by(name=name).first_or_404()
        user = Users.query.filter_by(id=login_session['users_id'])
        form = ItemForm()
        if category.users_id != login_session['users_id'] and not user.admin:
            flash(' You are not authorized add items to that category.')
            return redirect(url_for('category.showCategory', category_id=category_id))
    if request.method == 'POST':
        itemslist = request.form['itemslist'].splitlines(True)
        category = Category.query.filter_by(name=name).first_or_404()
        for item in itemslist:
            newItem = Item(item, "", "", "",    category.id, login_session['users_id'])
            db.session.add(newItem)
            db.session.commit() 
            flash('New Category %s Successfully Created' % category.name)
        return redirect(url_for('category.showHome'))
    else:
        return render_template('areanewItem.html', category=category, form=form)

@category.context_processor
def provideUser():
    if 'username' in login_session:
        try:
            loginuser = Users.query.filter_by(id=login_session['users_id']).first_or_404()
            return {'loginuser': loginuser,}
        except DatabaseError:
            return "The database may be sleeping. Try reloading the page."
    else:
        return {'loggedin': False,}


@category.route('/item/<name>/edit/', methods=['GET','POST'])
def editItem(name):
    if 'username' not in login_session:
        return redirect('/login')    
    else:
        item = Item.query.filter_by(name=name).first_or_404()
        user = Users.query.filter_by(id=login_session['users_id']).first_or_404()
        if item.users_id != login_session['users_id'] and not user.admin:
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
    else:
        item = Item.query.filter_by(name=name).first_or_404()
        user = Users.query.filter_by(id=login_session['users_id'])
        if item.users_id != login_session['users_id'] and not user.admin:
            category = Category.query.filter_by(id=item.category_id).first_or_404()
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
