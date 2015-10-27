from flask import Flask, render_template, request, redirect, url_for, flash, jsonify

from itemcatalog import app

@app.route('/')
@app.route('/category/')
def showCatagory():
	return 'The category page will show catagories and recent items.'


@app.route('/login/')
def showLogin():
	return 'Users will login here.'


@app.route('/disconnect')
def disconnect():
	return 'Users will disconnect here.'


@app.route('/user/<int:user_id>')
def showUser(user_id):
	#Should user profile be invisible? Perhaps. Then no number
	return 'Users will see profiles here.'


@app.route('/category/add')
def addCategory():
	return 'Add categories here.'


@app.route('/category/<int:category_id>/edit/')
def editCategory(category_id):
	return 'Edit categories here.'


@app.route('/category/<int:category_id>/delete/')
def deleteCategory(category_id):
	return 'Delete a category here.'


@app.route('/item/<int:item_id>/')
def showItem(item_id):
	return 'The item page will a particular item.'


@app.route('/item/add/')
def addItem():
	return 'Add an item here.'


@app.route('/item/<int:item_id>/edit/')
def editItem(item_id):
	return 'Edit an item here.'


@app.route('/item/<int:item_id>/delete')
def deleteItem(item_id):
	return 'Delete a item here.'
