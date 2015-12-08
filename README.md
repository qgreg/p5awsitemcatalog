Item Catalog

Item catalog allows users logged in with either Google or Facebook to contribute to a database of categories and items. 

Features:
  * Create, view, edit and delete categories.
  * Create, view, edit and delete items within the categories.
  * Login and create an account using Google or Facebook signins.
  * Users and admins can contribute categories and items.
  * View recently added items.
  * Add a list of items at once.
  * Add, view and link to Amazon products as images for items.
  * View categories added by a user.


Install
_______

The github repository is ready to deploy a beta version via heroku. For more information about heroku deployment visit: https://devcenter.heroku.com/articles/github-integration

For a distinct deployment, be sure to replace the database location by changing SQLALCHEMY_DATABASE_URI in config.py.


Deployment
__________

Item catalog is currently deployed at:
https://itemcataloggqw.herokuapp.com


API
___

JSON of all catagories is available at:
https://itemcatalog.herokuapp.com/catagory/JSON

JSON of all items in a catagories are available at:
https://itemcatalog.herokuapp.com//category/<name>/JSON

JSON of an item is available at:
https://itemcatalog.herokuapp.com//category/<categoryname>/item/<itemname>/JSON


Credits
_______

This project was developed as a part of my participation in the Full Stack Developer Nanodegree. Original work by Greg Quinlan
QuinlanGL@gmail.com


Thanks
------

Thanks to Udacity's Introduction to Relational Databases, Full Stack Foundations and Authentication and Authorization courses.