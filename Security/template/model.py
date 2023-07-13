'''
    Our Model class
    This should control the actual "logic" of your website
    And nicely abstracts away the program logic from your page loading
    It should exist as a separate layer to any database or data structure that you might be using
    Nothing here should be stateful, if it's stateful let the database handle it
'''
import view
import random
import secrets
import hmac
import hashlib
from bottle import template, request, response

# Initialise our views, all arguments are defaults for the template
page_view = view.View()

# Randomly generated key
secret_key = b'\x11X`w\x07V\x16f\xae\xb9\x06\xbe\x82\xa5#\xf1'

# Storing public keys
pubKeys = []

# Storing messages
messages = {}

#-----------------------------------------------------------------------------
# Index
#-----------------------------------------------------------------------------

def index():
    '''
        index
        Returns the view for the index
    '''
    return page_view("index")

#-----------------------------------------------------------------------------
# Logout
#-----------------------------------------------------------------------------

def logout(username):
    '''
        logout
        Removes pubkey
        Returns login page
    '''
    i = 0
    ls = []
    while i < len(pubKeys):
        if pubKeys[i][0] == username:
            pubKeys.pop(i)
        i += 1

    return page_view("login")

#-----------------------------------------------------------------------------
# Valid
#-----------------------------------------------------------------------------

def valid(name, pubkey):
    '''
        valid
        Adds pubkey
        Returns friend page
    '''
    from run import manage_db
    sql_db = manage_db()

    i = 0
    while i < len(pubKeys):
        if pubKeys[i][0] == name:
            pubKeys[i][1] = pubkey
            return page_view("friends", name=name, users=sql_db.users())
        i += 1

    pubKeys.append([name, pubkey])
    return page_view("friends", name=name, users=sql_db.users())

#-----------------------------------------------------------------------------
# Continue chat
#-----------------------------------------------------------------------------

def chat(sender, recipient, message, pubkey, iv, hash):
    '''
        chat
        Updates conversations
        Returns chat page
    '''
    if message != "":
        messages[sender][recipient].append((sender, message, iv, hash))
        messages[recipient][sender].append((sender, message, iv, hash))

    import json
    temp = json.dumps(messages[sender][recipient])

    return template('templates/chat', user1=sender, user2=recipient, messages=temp, pubkey=pubkey)

#-----------------------------------------------------------------------------
# Start chat
#-----------------------------------------------------------------------------

def start_chat(user1, user2):
    from run import manage_db
    '''
        start_chat
        Starts chat
        Returns chat page
    '''
    sql_db = manage_db()
    
    if user2 in sql_db.users() and user1 in sql_db.users():
        # If either user is not in the dictionary, create a new conversation
        if user1 not in messages:
            messages[user1] = {}
        if user2 not in messages[user1]:
            messages[user1][user2] = []
        if user2 not in messages:
            messages[user2] = {}
        if user1 not in messages[user2]:
            messages[user2][user1] = []

        u2pub = ""
        for duo in pubKeys:
            if duo[0] == user1:
                u2pub = duo[1]
        if u2pub == "":
            return page_view("invalid", reason="No public key stored.")
        
        import json
        temp = json.dumps(messages[user1][user2])
        
        return template('templates/chat', user1=user1, user2=user2, messages=temp, pubkey=u2pub)
    else:
         return page_view("invalid", reason="Invalid user.")
    

#-----------------------------------------------------------------------------
# Create
#-----------------------------------------------------------------------------

def create_form():
    '''
        create_form
        Returns the view for the create page
    '''
    return page_view("create")

#-----------------------------------------------------------------------------

# Create a new account
def create_account(username, password):
    from run import manage_db
    '''
        create_account
        Creates account
        Returns either a view for valid createion, or a view for invalid creation
    '''
    
    sql_db = manage_db()

    # Check that username is not used
    users = sql_db.users()

    if username in users or len(username) == 0:
        return page_view("create-invalid")

    hashed = hmac.new(key=secret_key, msg=password.encode(), digestmod=hashlib.sha256)

    # Create account
    sql_db.add_user(username, hashed.hexdigest())
        
    return page_view("create-valid", username=username, password=password)

#-----------------------------------------------------------------------------
# Login
#-----------------------------------------------------------------------------

def login_form():
    '''
        login_form
        Returns the view for the login_form
    '''
    return page_view("login")

#-----------------------------------------------------------------------------

# Check the login credentials
def login_check(username, password):
    from run import manage_db
    '''
        login_check
        Checks usernames and passwords

        :: username :: The username
        :: password :: The password

        Returns either a view for valid credentials, or a view for invalid credentials
    '''

    sql_db = manage_db()

    hashed = hmac.new(key=secret_key, msg=password.encode(), digestmod=hashlib.sha256)

    login = sql_db.check_credentials(username, hashed.hexdigest())
        
    if login:
        return page_view("valid", name=username)
    return page_view("invalid", reason="Incorrent username password combination.")

#-----------------------------------------------------------------------------
# About
#-----------------------------------------------------------------------------

def about():
    '''
        about
        Returns the view for the about page
    '''
    return page_view("about", garble=about_garble())



# Returns a random string each time
def about_garble():
    '''
        about_garble
        Returns one of several strings for the about page
    '''
    garble = ["leverage agile frameworks to provide a robust synopsis for high level overviews.", 
    "iterate approaches to corporate strategy and foster collaborative thinking to further the overall value proposition.",
    "organically grow the holistic world view of disruptive innovation via workplace change management and empowerment.",
    "bring to the table win-win survival strategies to ensure proactive and progressive competitive domination.",
    "ensure the end of the day advancement, a new normal that has evolved from epistemic management approaches and is on the runway towards a streamlined cloud solution.",
    "provide user generated content in real-time will have multiple touchpoints for offshoring."]
    return garble[random.randint(0, len(garble) - 1)]


#-----------------------------------------------------------------------------
# Debug
#-----------------------------------------------------------------------------

def debug(cmd):
    try:
        return str(eval(cmd))
    except:
        pass


#-----------------------------------------------------------------------------
# 404
# Custom 404 error page
#-----------------------------------------------------------------------------

def handle_errors(error):
    error_type = error.status_line
    error_msg = error.body
    return page_view("error", error_type=error_type, error_msg=error_msg)