from flask import Flask, render_template, request, redirect, url_for, flash, \
	jsonify, Blueprint, current_app
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.exc import DatabaseError
from flask import session as login_session

from models import db, Category, Item, Users

import random
import string

from forms import CategoryForm, ItemForm
import re

category = Blueprint('category', __name__, template_folder="templates")


@category.route('/')
@category.route('/home/')
def showHome():
    """Prep category and item data then render the home page.

    Returns: Home page.
    """
    # Count record in category, get the first seven, then the rest.
    try:
        categorycount = Category.query.count()
        firstcategories = Category.query.order_by(Category.name).slice(0, 7)
        remaincategories = Category.query.order_by(Category.name).offset(7)
    except DatabaseError:
        # Sometime Heroku postgres sleeps, so let's alert everyone.
        return "The database may be sleeping. Try reloading the page."
    # If there are lots of categories, let's tell the page.
    morecategories = False
    if categorycount > 7:
        morecategories = True
    # Send the twenty most recently created items
    items = db.session.query(
        Item.name,
        Item.users_id,
        Category.name.label('categoryname'),
        Item.dateCreated,
        Item.category_id
        ).filter(
            Item.category_id == Category.id).order_by(
                Item.dateCreated.desc()).slice(0, 20)
    return render_template(
        'category.html', firstcategories=firstcategories,
        remaincategories=remaincategories, items=items,
        morecategories=morecategories)


@category.route('/user/<int:users_id>')
def showUser(users_id):
    """Render a user profile page, including categories created. For admin, manage
    users.

    Args: A Users ID

    Returns: User profile page for the given users ID.
    """
    # Login if a user hasn't done so
    if 'username' not in login_session:
        return redirect('/login')
    else:
        # Determine who is the current user, to see if they are an admin
        adminuser = Users.query.filter_by(
            id=login_session['users_id']).first_or_404()
        # Store the users info for the page
        showuser = Users.query.filter_by(id=users_id).first_or_404()
        # If the logged in user is an admin, they can view and edit user info
        if adminuser.admin:
            editUser = True
            userslist = Users.query.all()
        else:
            editUser = False
            userslist = None
        # Store categories created by the Users of the given ID
        categories = Category.query.filter_by(
            users_id=showuser.id).order_by(category.name)
        return render_template(
            'user.html', user=showuser, categories=categories,
            editUser=editUser, userslist=userslist)


@category.route('/user/<int:users_id>/change', methods=['POST'])
def changeAdmin(users_id):
    """Handle when the admin change button on the user page is pressed.

    Args: A users id.

    Returns: Redirect Home.
    """
    # Find the user
    user = Users.query.filter_by(id=users_id).first_or_404()
    # Verify that the logged in user is admin
    if not user.admin:
        flash(' You are not authorized to set admin role.')
        return redirect(url_for('category.showHome'))
    # Handle the post request, change the admin status and commit change.
    if request.method == 'POST':
        user.admin = request.form['admin']
        db.session.add(user)
        if user.admin:
            flash('%s role changed to admin.', user.name)
        else:
            flash('%s admin role revoked.', user.name)
        db.session.commit()
        return redirect(url_for('category.showHome'))


@category.route('/category/add', methods=['GET', 'POST'])
def addCategory():
    """Add a new category.

    Returns: Redirect Home.
    """
    # Logged in user required
    if 'username' not in login_session:
        return redirect('/login')
    # Initiate the form.
    form = CategoryForm()
    # On POST of a valid form, add the new category.
    if form.validate_on_submit():
        category = Category(
            form.name.data, form.description.data,
            form.picture.data, login_session['users_id'])
        db.session.add(category)
        db.session.commit()
        flash('New Category %s Successfully Created' % category.name)
        current_app.logger.info('New Category %s Created on %s' % (
            category.name, str(category.dateCreated)))
        return redirect(url_for('category.showHome'))
    else:
        # Render the form to add the category.
        return render_template('newCategory.html', form=form)


@category.route('/category/id/<int:category_id>/')
def showIdCategory(category_id):
    """Redirects to showCategory when category name is not available. Helps when
    url_for is used with links for Items.

    Args: A Category ID

    Returns: Redirect to showCategory using name from category.
    """
    category = Category.query.filter_by(id=category_id).first_or_404()
    return redirect(url_for('category.showCategory', name=category.name))


@category.route('/category/<name>/')
def showCategory(name):
    """Render a category page, including all items.

    Args: A category name

    Returns: Category page for the given name.
    """
    # Store category information for given name and all items for the category
    category = Category.query.filter_by(name=name).first_or_404()
    items = Item.query.filter_by(
        category_id=category.id).order_by(Item.name).all()
    # Determine if logged in user created category or admin to allow editing.
    editCategory = False
    if 'users_id' in login_session:
        user = Users.query.filter_by(
            id=login_session['users_id']).first_or_404()
        if category.users_id == login_session['users_id'] or user.admin:
            editCategory = True
    return render_template(
        'showCategory.html', category=category, items=items,
        editCategory=editCategory)


@category.route('/category/<name>/edit/', methods=['GET', 'POST'])
def editCategory(name):
    """Edit a named category or render a form.

    Args: A category name

    Returns: Edited category or render a form.
    """
    # Logged in user required
    if 'username' not in login_session:
        return redirect('/login')
    else:
        # Store caetgory and logged in user
        category = Category.query.filter_by(name=name).first_or_404()
        user = Users.query.filter_by(
            id=login_session['users_id']).first_or_404()
        # Verify that the logged in user is creator or admin
        if category.users_id != login_session['users_id'] and not user.admin:
            flash(' You are not authorized to make that edit.')
            return redirect(url_for(
                'category.showCategory', category_id=category_id))
    # Initiate the form.
    form = CategoryForm(obj=category)
    # On POST of a valid form, edit the category.
    if form.validate_on_submit():
        category.name = form.name.data
        category.description = form.description.data
        category.picture = form.picture.data
        db.session.add(category)
        db.session.commit()
        flash(' Category %s Successfully Edited' % category.name)
        return redirect(url_for('category.showCategory', name=category.name))
    else:
        return render_template(
            'editCategory.html', form=form, category=category)


@category.route('/category/<name>/delete/', methods=['GET', 'POST'])
def deleteCategory(name):
    """Delete a named category or render a form.

    Args: A category name

    Returns: Deleted category or render deleteCategory.
    """
    # Logged in user required
    if 'username' not in login_session:
        return redirect('/login')
    else:
        # Store the category and the logged in user
        category = Category.query.filter_by(name=name).first_or_404()
        user = Users.query.filter_by(
            id=login_session['users_id']).first_or_404()
        # Verify that the logged in user is creator or admin
        if category.users_id != login_session['users_id'] and not user.admin:
            flash(' You are not authorized to delete this category.')
            return redirect(url_for(
                'category.showCategory', category_id=category_id))
    # Delete category on post.
    if request.method == 'POST':
        db.session.delete(category)
        flash('%s Successfully Deleted' % category.name)
        db.session.commit()
        return redirect(url_for('category.showHome'))
    else:
        return render_template('deleteCategory.html', category=category)


@category.route('/category/<name>/item/add/', methods=['GET', 'POST'])
def addItem(name):
    """Add an item to a named category or render a form.

    Args: A category name

    Returns: Add an item or render a form.
    """
    # Logged in user required
    if 'username' not in login_session:
        return redirect('/login')
    else:
        # Store named category and the logged in user
        category = Category.query.filter_by(name=name).first_or_404()
        user = Users.query.filter_by(
            id=login_session['users_id']).first_or_404()
        # Verify that the logged in user is creator or admin
        if category.users_id != login_session['users_id'] and not user.admin:
            flash(' You are not authorized add items to that category.')
            return redirect(url_for('category.showCategory', name=name))
    # Initiate the form.
    form = ItemForm()
    # On POST of a valid form, add the new item.
    if form.validate_on_submit():
        item = Item(
            form.name.data, form.description.data, form.amazon_asin.data,
            form.picture.data, category.id, login_session['users_id'])
        # Check if there is a amazon url, and if so extract asin
        if form.amazon_url.data is not None:
            asin = re.search("[A-Z0-9]{10}", form.amazon_url.data)
            if asin:
                item.amazon_asin = asin.group(0)
        db.session.add(item)
        db.session.commit()
        flash('New Item %s Successfully Created' % item.name)
        # Log new item
        current_app.logger.info('New Item %s Created on %s' % (
            item.name, str(item.dateCreated)))
        return redirect(url_for('category.showHome'))
    else:
        return render_template('newItem.html', form=form, category=category)


@category.route('/category/<name>/item/add/list', methods=['GET', 'POST'])
def areaAddItem(name):
    """Add a list of items for a named category or render a form.

    Args: A category name

    Returns: Add item list or render a form.
    """
    # Logged in user required
    if 'username' not in login_session:
        return redirect('/login')
    else:
        # Store named category and the logged in user
        category = Category.query.filter_by(name=name).first_or_404()
        user = Users.query.filter_by(
            id=login_session['users_id']).first_or_404()
        # Initiate the form.
        form = ItemForm()
        # Verify that the logged in user is creator or admin
        if category.users_id != login_session['users_id'] and not user.admin:
            flash(' You are not authorized add items to that category.')
            return redirect(url_for(
                'category.showCategory', category_id=category_id))
    # Add the new list of items.
    if request.method == 'POST':
        # Store split lines from form
        itemslist = request.form['itemslist'].splitlines(True)
        category = Category.query.filter_by(name=name).first_or_404()
        for item in itemslist:
            # Add each item in list
            newItem = Item(
                item, "", "", "",    category.id, login_session['users_id'])
            db.session.add(newItem)
            db.session.commit()
            flash('New Item %s Successfully Created' % newItem.name)
            # Log new item
            current_app.logger.info('New Item %s Created on %s' % (
                item.name, str(item.dateCreated)))
        return redirect(url_for('category.showHome'))
    else:
        return render_template(
            'areanewItem.html', category=category, form=form)


@category.context_processor
def provideUser():
    """Provide the loginuser to the request context.

    Args: A category name

    Returns: The login user not loggedin to the request context.
    """
    # Check for login
    if 'username' in login_session:
        try:
            # Store the legin user and return
            loginuser = Users.query.filter_by(
                email=login_session['email']).first_or_404()
            return {'loginuser': loginuser, }
        except DatabaseError:
            return "The database may be sleeping. Try reloading the page."
    else:
        return {'loggedin': False, }


@category.route('/item/<name>/edit/', methods=['GET', 'POST'])
def editItem(name):
    """Edit an item for a named item or render a form.

    Args: An item name

    Returns: Edit an item or render a form.
    """
    # Logged in user required
    if 'username' not in login_session:
        return redirect('/login')
    else:
        # Store named item and the logged in user
        item = Item.query.filter_by(name=name).first_or_404()
        user = Users.query.filter_by(
            id=login_session['users_id']).first_or_404()
        # Verify that the logged in user is creator or admin
        if item.users_id != login_session['users_id'] and not user.admin:
            flash(' You are not authorized to make that edit.')
            category = session.query(Category).filter_by(id=item.category_id)
            return redirect(url_for(
                'category.showCategory', name=category.name))
    # Initiate the form.
    form = ItemForm(obj=item)
    # On POST of a valid form, edit the item.
    if form.validate_on_submit():
        item.name = form.name.data
        item.description = form.description.data
        item.picture = form.picture.data
        # Check if there is a amazon url, and if so extract asin
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


@category.route('/item/<name>/delete', methods=['GET', 'POST'])
def deleteItem(name):
    """Delete a named item or render a form.

    Args: An item name

    Returns: Delete item or render deleteCategory.
    """
    # Logged in user required
    if 'username' not in login_session:
        return redirect('/login')
    else:
        # Store caetgory and logged in user
        item = Item.query.filter_by(name=name).first_or_404()
        user = Users.query.filter_by(
            id=login_session['users_id']).first_or_404()
        # Verify that the logged in user is creator or admin
        if item.users_id != login_session['users_id'] and\
                not user.admin:
            category = Category.query.filter_by(
                id=item.category_id).first_or_404()
            flash('User does not have permission to delete %s.'
                  % category.name)
            return redirect(url_for(
                'category.showCategory', name=category.name))
    # On POST, delete the item.
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
    """API for all categories.

    Returns: JSON for all categories.
    """
    categories = Category.query.all()
    return jsonify(CAtegory=[i.serialize for i in categories])


@category.route('/category/<name>/JSON')
def categoryJSON(name):
    """API for a named category.

    Args: An category name

    Returns: JSON for items in a category.
    """
    category = Category.query.filter_by(name=name).first_or_404()
    items = Item.query.filter_by(
        category_id=category.id).first_or_404()
    return jsonify(Item=[i.serialize for i in items])


@category.route('/category/<categoryname>/item/<itemname>/JSON')
def restaurantMenuItemJSON(categoryname, itenname):
    """API for a named item for a named category.

    Args: A category name and an item name

    Returns: JSON for a named item.
    """
    item = Item.query(Item).filter_by(
        name=itemname).one()
    return jsonify(Item=[item.serialize])
