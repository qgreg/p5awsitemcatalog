from flask import Flask, render_template, request, redirect, url_for, flash, \
    jsonify, Blueprint, make_response

from datetime import datetime

from flask import session as login_session
import random
import string

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
import requests

from itemcatalog.category.models import db, Users

# Define login_blueprint
login_blueprint = Blueprint(
    'login', __name__,
    template_folder="templates")

GOOGLE_CLIENT_SECRETS = '/var/www/itemcatalog/client_secrets.json'
FB_CLIENT_SECRETS = '/var/www/itemcatalog/fb_client_secrets.json'

CLIENT_ID = json.loads(
    open(GOOGLE_CLIENT_SECRETS, 'r').read())['web']['client_id']
APPLICATION_NAME = "Item Catalog"



@login_blueprint.route('/login')
def showLogin():
    """Create a state token to prevent request forgery, Store it in login_session
    for later validation.

    Returns:
        Login page.
    """

    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


@login_blueprint.route('/fbconnect', methods=['POST'])
def fbconnect():
    """Confirm connection with Facebook, collect user info and store key logout
    info. Register user if new.

    Returns: Login acknowledgement.
    """

    # Confirm state token, then record access_token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data
    print "access token received %s " % access_token

    # Send app_id and app_secret
    app_id = json.loads(open(FB_CLIENT_SECRETS, 'r').read())[
        'web']['app_id']
    app_secret = json.loads(
        open(FB_CLIENT_SECRETS, 'r').read())['web']['app_secret']
    url = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s'\
        % (app_id, app_secret, access_token)  # noqa
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    # Use token to get user info from API
    userinfo_url = "https://graph.facebook.com/v2.4/me"
    # strip expire tag from access token
    token = result.split("&")[0]

    # Get user fields, store in login session
    url = 'https://graph.facebook.com/v2.4/me?%s&fields=name,id,email' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    # print "url sent for API access:%s"% url
    print "API JSON result: %s" % result
    data = json.loads(result)
    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]

    # The token must be stored in the login_session in order to properly
    # logout, let's strip out the information before the equals sign in our
    # token
    stored_token = token.split("=")[1]
    login_session['access_token'] = stored_token

    # Get user picture
    url = 'https://graph.facebook.com/v2.4/me/picture?%s&redirect=0&height=200&width=200' % token  # noqa
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)
    print data
    login_session['picture'] = data["data"]["url"]

    # see if user exists, then store user id
    users_id = getUsersID(login_session['email'])
    if not users_id:
        users_id = createUsers(login_session)
    login_session['users_id'] = users_id

    # Output login acknowledgement
    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;'
    output += '-webkit-border-radius: 150px;-moz-border-radius: 150px;">'
    flash("Now logged in as %s" % login_session['username'])
    return output


@login_blueprint.route('/fbdisconnect')
def fbdisconnect():
    """Posts logout with Facebook using Facebook ID and access token.

    Returns: Logout acknowledgement.
    """

    # Send id and access token to Facebook to delete login
    facebook_id = login_session['facebook_id']
    # The access token must me included to successfully logout
    access_token = login_session['access_token']
    url = 'https://graph.facebook.com/%s/permissions?access_token=%s' \
          % (facebook_id, access_token)
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    return "You have been logged out"


@login_blueprint.route('/gconnect', methods=['POST'])
def gconnect():
    """Manage sign in connection with Google, using state token and auth code to
    obtain access token for the correct user ID number. Collect user info and
    store key logout info. Register user if new.

    Returns: Login acknowledgement.
    """
    # Confirm state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Collect auth code
    code = request.data
    # Exchange auth code for access token
    try:
        oauth_flow = flow_from_clientsecrets(GOOGLE_CLIENT_SECRETS, scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(json.dumps(
            'Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify if user if already connected
    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(
            json.dumps('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['credentials'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['provider'] = 'google'
    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # Get users_id of user, create new one if none exists
    email = login_session['email']
    users_id = getUsersID(email)
    if users_id is None:
        users_id = createUsers(login_session)
    login_session['users_id'] = users_id

    # Acknowledge login
    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: '
    output += '150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;">'
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output


@login_blueprint.route('/disconnect')
def disconnect():
    """Perform provider specific logout then delete stored user information.

    Returns: Redirects to home.
    """

    # Perform provider based disconnects
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
        if login_session['provider'] == 'facebook':
            fbdisconnect()
            del login_session['facebook_id']

        # Delete user information
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['users_id']
        del login_session['provider']

        flash("You have successfully logged out.")
        return redirect(url_for('category.showHome'))
    else:
        flash("You are not currently logged in.")
        return redirect(url_for('category.showHome'))


@login_blueprint.route('/gdisconnect')
def gdisconnect():
    """Revoke Google login for a connected user.

    Returns: Logout acknowledgement.
    """

    # Only disconnect a connected user
    credentials = login_session.get('credentials')
    if credentials is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Revoke google login
    access_token = credentials
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    # Confirm successful logout
    if result['status'] == '200':
        # Reset the user's sesson.
        del login_session['credentials']
        # Acknowledge disconnection
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        # For whatever reason, the given token was invalid.
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


def createUsers(login_session):
    """Create a new User record from login information.

    Args: The Flask session as login_session

    Returns: New Users ID number.
    """

    newUser = Users(name=login_session['username'],
                    email=login_session['email'],
                    picture=login_session['picture'],
                    admin = False)
    db.session.add(newUser)
    db.session.commit()
    users = db.session.query(Users).filter_by(email=login_session['email']).one()
    return users.id


def getUsersInfo(users_id):
    """Returns a Users record from a Users ID.

    Args: A Users ID

    Returns: A Users record.
    """

    users = Users.query.filter_by(id=users_id).first_or_404()
    return users


def getUsersID(email):
    """Find a Users ID, if it exists, from a Users email.

    Args: An email address

    Returns: The Users ID number.
    """
    try:
        users = Users.query.filter_by(email=email).first_or_404()
        return users.id
    except:
        return None
