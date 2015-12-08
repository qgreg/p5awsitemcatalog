from flask_wtf import Form
from wtforms import StringField, validators


class CategoryForm(Form):
    name = StringField(
        'Name', [validators.Length(min=4, max=250, message="name problem")])
    description = StringField('Description', [validators.Length(
            max=250, message="description problem")])
    picture = StringField('Picture URL', [
        validators.Optional(), validators.Length(
            max=250, message="picture length problem"),
        validators.url(message="Must enter a valid url.")])


class ItemForm(Form):
    name = StringField('Name', [validators.Length(min=4, max=250)])
    description = StringField('Description', [validators.Length(max=250)])
    picture = StringField('Picture URL', [
        validators.Optional(), validators.Length(max=250),
        validators.url(message="Must enter a valid url.")])
    # ASIN corresponds to a Amazon product number. App generates image and link
    amazon_asin = StringField('Amazon ASIN', [
        validators.Optional(), validators.Length(max=250),
        validators.Regexp("[A-Z0-9]{10}", message="Must enter a valid ASIN.")])
    # Allows user to enter url of Amazon product page. App extracts ASIN.
    amazon_url = StringField('Amazon URL', [
        validators.Optional(), validators.Length(max=250),
        validators.url(message="Must enter a valid url.")])
