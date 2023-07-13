'''
    This file will handle our typical Bottle requests and responses 
    You should not have anything beyond basic page loads, handling forms and 
    maybe some simple program logic
'''

from bottle import route, get, post, error, request, static_file, redirect

import bottle_session

import model

import hashlib

import view
page_view = view.View()

#-----------------------------------------------------------------------------
# Static file paths
#-----------------------------------------------------------------------------

# Allow image loading
@route('/img/<picture:path>')
def serve_pictures(picture):
    '''
        serve_pictures

        Serves images from static/img/

        :: picture :: A path to the requested picture

        Returns a static file object containing the requested picture
    '''
    return static_file(picture, root='static/img/')

#-----------------------------------------------------------------------------

# Allow CSS
@route('/css/<css:path>')
def serve_css(css):
    '''
        serve_css

        Serves css from static/css/

        :: css :: A path to the requested css

        Returns a static file object containing the requested css
    '''
    return static_file(css, root='static/css/')

#-----------------------------------------------------------------------------

# Allow javascript
@route('/js/<js:path>')
def serve_js(js):
    '''
        serve_js

        Serves js from static/js/

        :: js :: A path to the requested javascript

        Returns a static file object containing the requested javascript
    '''
    return static_file(js, root='static/js/')

#-----------------------------------------------------------------------------
# Pages
#-----------------------------------------------------------------------------

# Redirect to login
@get('/')
@get('/home')
def get_index():
    '''
        get_index
        
        Serves the index page
    '''
    return model.index()

#-----------------------------------------------------------------------------

# Logout
@get('/logout')
def get_logout(session):
    '''
        get_logout
        
        Serves the logout page
        Processes logout
    '''
    if session['name'] != None:
        username = session['name']
        session['name'] = 'None'
        
        return model.logout(username)
    else: 
        return page_view("invalid", reason="Not logged in")

#-----------------------------------------------------------------------------

# Display the login page
@get('/login')
def get_login_controller(session):
    '''
        get_login
        
        Serves the login page
        Serves friend page if logged in
    '''
    if session['name'] != None and session['name'] != 'None':
        from run import manage_db
        sql_db = manage_db()
        return page_view("friends", name=session['name'], users=sql_db.users())
    
    return model.login_form()

#-----------------------------------------------------------------------------

# Attempt the login
@post('/login')
def post_login(session):
    '''
        post_login
        
        Handles login attempts
        Expects a form containing 'username' and 'password' fields
    '''

    if session['tries'] == None:
        session['tries'] = 0

    if int(session['tries']) > 3:
        return page_view("invalid", reason="Too many tries.")
    
    username = request.forms.get('username')
    password = request.forms.get('password')

    session['tries'] = int(session['tries']) + 1
    
    # Call the appropriate method
    return model.login_check(username=username, password=password)

#-----------------------------------------------------------------------------

# Chat
@route('/chat/<user1>/<user2>', method='POST')
def chat(session, user1, user2):
    '''
        chat
        
        Handles the chat session
        Expects a form containing 'sender', 'recipient', 'message', 'pubkey', 'iv' and 'hash' fields
    '''
    sender = request.forms.get('sender')
    recipient = request.forms.get('recipient')
    message = request.forms.get('message')
    pubkey = request.forms.get('pubkey')
    iv = request.forms.get('iv')
    hash = request.forms.get('hash')

    if session['name'] != sender:
        return page_view("invalid", reason="Incorrect user.")

    return model.chat(sender=sender, recipient=recipient, message=message, pubkey=pubkey, iv=iv, hash=hash)
    
#-----------------------------------------------------------------------------

# Find user to chat with
@post('/friends')
def post_friends(session):
    '''
        post_friends
        
        Expects a form containing 'current' and 'username' fields
    '''
    current = request.forms.get('current')
    username = request.forms.get('username')

    if session['name'] != current:
        return page_view("invalid", reason="Incorrect user.")

    return model.start_chat(current, username)

#-----------------------------------------------------------------------------

# Confirm login
@post('/valid')
def post_valid(session):
    '''
        post_valid
        
        Expects a form containing 'current' and 'pubkey' fields
    '''
    current = request.forms.get('current')
    pubkey = request.forms.get('pubkey')

    session['tries'] = 0
    session['name'] = current

    # Call the appropriate method
    return model.valid(current, pubkey)

#-----------------------------------------------------------------------------

# Display the login page
@get('/create-invalid')
def get_create_controller():
    '''
        get_create_controller
        
        Serves the invalid create page
    '''
    return model.create_form()

#-----------------------------------------------------------------------------

# Create Account
@post('/create-invalid')
def post_create():
    '''
        post_create
        
        Handles creating new accounts
    '''

    # Handle the form processing
    username = request.forms.get('username')
    password = request.forms.get('password')
    
    # Call the appropriate method
    return model.create_account(username, password)

#-----------------------------------------------------------------------------

# Display the login page
@get('/create')
def get_create_controller():
    '''
        get_create_controller
        
        Serves the create page
    '''
    return model.create_form()

#-----------------------------------------------------------------------------

# Create Account
@post('/create')
def post_create():
    ''''
        post_create
        
        Handles creating new accounts
    '''

    username = request.forms.get('username')
    password = request.forms.get('password')
    
    return model.create_account(username, password)


#-----------------------------------------------------------------------------

@get('/about')
def get_about():
    '''
        get_about
        
        Serves the about page
    '''
    return model.about()
#-----------------------------------------------------------------------------

# Help with debugging
@post('/debug/<cmd:path>')
def post_debug(cmd):
    return model.debug(cmd)

#-----------------------------------------------------------------------------

# 404 errors, use the same trick for other types of errors
@error(404)
def error(error): 
    return model.handle_errors(error)
