from flask_wtf import Form
from wtforms import StringField, validators

class CategoryForm(Form):
    name     = StringField('Name', [validators.Length(min=4, max=250)])
    description = StringField('Description', [validators.Length(max=250)])
    picture = StringField('Picture URL', [validators.Length(max=250)])


class ItemForm(Form):
    name     = StringField('Name', [validators.Length(min=4, max=250)])
    description = StringField('Description', [validators.Length(max=250)])
    picture = StringField('Picture URL', [validators.Length(max=250)])
    