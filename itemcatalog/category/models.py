import os
import sys

from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

from datetime import datetime


db = SQLAlchemy()


class Users(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(250), unique=True)
    picture = db.Column(db.String(250))
    admin = db.Column(db.Boolean)

    def __init__(self, name, email, picture, admin):
        self.name = name
        self.email = email
        self.picture = picture
        self.admin = admin

    def __repr__(self):
        return '<Users %r>' % self.name


class Category(db.Model):
    name = db.Column(db.String(250), nullable=False, unique=True)
    description = db.Column(db.String(250))
    picture = db.Column(db.String(250))
    dateCreated = db.Column(db.Date)
    id = db.Column(db.Integer, primary_key=True)
    users = db.relationship('Users')
    users_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __init__(self, name, description, picture, users_id, dateCreated=None):
        self.name = name
        self.description = description
        self.picture = picture
        self.users_id = users_id
        if dateCreated is None:
            self.dateCreated = datetime.now()

    def __repr__(self):
        return '<Category %r>' % self.name

    @property
    def serialize(self):
        # Returns object data in easily serializable format
        return {
            'name': self.name,
            'description': self.description,
            'dateCreated': str(self.dateCreated),
            'id': self.id,
            'picture': self.picture,
        }


class Item(db.Model):
    name = db.Column(db.String(80), nullable=False)
    id = db.Column(db.Integer, primary_key=True)
    dateCreated = db.Column(db.Date)
    description = db.Column(db.String(250))
    # ASIN corresponds to a Amazon product number. App generate image and link
    amazon_asin = db.Column(db.String(250))
    picture = db.Column(db.String(250))
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    users_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    category = db.relationship('Category')
    users = db.relationship('Users')

    def __init__(
            self, name, description, amazon_asin,
            picture, category_id, users_id, dateCreated=None):
        self.name = name
        self.description = description
        self.amazon_asin = amazon_asin
        self.picture = picture
        self.category_id = category_id
        self.users_id = users_id
        if dateCreated is None:
            self.dateCreated = datetime.now()

    def __repr__(self):
        return '<Item %r>' % self.name

    @property
    def serialize(self):
        # Returns object data in easily serializable format
        return {
            'name': self.name,
            'description': self.description,
            'dateCreated': str(self.dateCreated),
            'id': self.id,
            'amazon_asin': self.amazon_asin,
            'picture': self.picture,
            'category_id': self.category_id,
        }
