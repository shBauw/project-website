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

# Storing courses
courses = []

# Thread structure [[user, anonymous], [user upvote, admin upvote], message]

# Muted users
muted = []

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

    uCourses = []
    for course in courses:
        if name in course[1]:
            uCourses.append(course[0])

    i = 0
    while i < len(pubKeys):
        if pubKeys[i][0] == name:
            pubKeys[i][1] = pubkey
            return page_view("friends", name=name, users=sql_db.users(), courses=uCourses)
        i += 1

    pubKeys.append([name, pubkey])
    return page_view("friends", name=name, users=sql_db.users(), courses=uCourses)

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
# Forum
#-----------------------------------------------------------------------------  

def enter_forum(user, course):
    from run import manage_db
    sql_db = manage_db()
    users = len(sql_db.users())

    threads = False
    for coursed in courses:
        if coursed[0] == course:
            if user in coursed[1] or sql_db.isAdmin(user):
                threads = []
                i = len(coursed[2])
                while i > 0:
                    if coursed[2][i-1][0][0] not in muted:
                        threads.append(coursed[2][i-1])
                    i = i - 1
            break
    if threads == False:
        return page_view("invalid", reason="Invalid course")
    else:
        import json
        return template('templates/forum', course=course, user=user, threads=json.dumps(threads))

def add_post(user, course):
    return page_view("write", user=user, course=course)

def write(user, course, anom, message):
    if message == "":
        return enter_forum(user, course)
    for c in courses:
        if c[0] == course:
            c[2].append([[user, anom], [0,0], message])
            return enter_forum(user, course)

def endorse(user, course, id):
    from run import manage_db
    sql_db = manage_db()

    print(id)
    for c in courses:
        if c[0] == course:
            if sql_db.isAdmin(user):
                c[2][int(id)][1][1] += 1
            else:
                c[2][int(id)][1][0] += 1
                if c[2][int(id)][1][0] > (len(sql_db.users()) / 10):
                    c[2][int(id)][1][1] = 1
            return enter_forum(user, course)
    

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
# Admin
#-----------------------------------------------------------------------------

def admin_form(user):
    '''
        admin_form
        Returns the view for the admin page
    '''
    from run import manage_db
    sql_db = manage_db()

    uCourses = []
    for course in courses:
        uCourses.append(course[0])

    return page_view("admin", name=user, users=sql_db.users(), courses=uCourses)

#-----------------------------------------------------------------------------

def edit_user(user1, user2):
    from run import manage_db
    '''
        start_chat
        Starts chat
        Returns chat page
    '''
    sql_db = manage_db()

    if not sql_db.isAdmin(user1): return page_view("invalid", reason="You are not an admin")

    if user2 in sql_db.users():
        admin = sql_db.isAdmin(user2)
        uCourses = []
        for course in courses:
            if user2 in course[1]:
                uCourses.append(course[0])
        mute = 0
        if user2 in muted:
            mute = 1

        return page_view('alter-user', user=user2, courses=uCourses, admin=admin[0], muted=mute)
    else:
         return page_view("invalid", reason="Invalid user.")
    
#-----------------------------------------------------------------------------

def edit_course(user1, course):
    from run import manage_db
    '''
        start_chat
        Starts chat
        Returns chat page
    '''
    sql_db = manage_db()

    if course == "":
        return page_view("admin", name=user1, users=sql_db.users(), courses=getCourses())
    
    if not sql_db.isAdmin(user1): return page_view("invalid", reason="You are not an admin")

    found = 'none'
    i = 0
    while i < len(courses):
        if courses[i][0] == course:
            found = i
            break
        i += 1

    print("FOUND: ", found);

    if found == 'none':
        found = len(courses)
        courses.append([course, [], []])

    return page_view("alter-course", course=courses[i][0], users=courses[i][1])

#-----------------------------------------------------------------------------

def user_addCourse(user, course):
    from run import manage_db
    sql_db = manage_db()

    mute = 0
    if user in muted:
        mute = 1

    if course == "":
        return page_view('alter-user', user=user, courses=uCourses, admin=admin, muted=mute)

    found = 'none'
    i = 0
    while i < len(courses):
        if courses[i][0] == course:
            courses[i][1].append(user)
            found = i
            break
        i += 1

    if found == 'none':
        found = len(courses)
        courses.append([course, [user], []])

    if user in sql_db.users():
        admin = sql_db.isAdmin(user)
        uCourses = []
        for course in courses:
            if user in course[1]:
                uCourses.append(course[0])

        return page_view('alter-user', user=user, courses=uCourses, admin=admin, muted=mute)

#-----------------------------------------------------------------------------

def user_removeCourse(user, course):
    from run import manage_db
    sql_db = manage_db()

    i = 0
    while i < len(courses):
        if courses[i][0] == course:
            courses[i][1].remove(user)
            break
        i += 1

    if user in sql_db.users():
        admin = sql_db.isAdmin(user)
        uCourses = []
        for course in courses:
            if user in course[1]:
                uCourses.append(course[0])

        mute = 0
        if user in muted:
            mute = 1

        return page_view('alter-user', user=user, courses=uCourses, admin=admin, muted=mute)
    
#-----------------------------------------------------------------------------

def makeAdmin(user, admin):
    from run import manage_db
    sql_db = manage_db()

    if admin == 'Y':
        sql_db.makeAdmin(user)
    elif admin == 'N':
        sql_db.remAdmin(user)

    if user in sql_db.users():
        admin = sql_db.isAdmin(user)
        uCourses = []
        for course in courses:
            if user in course[1]:
                uCourses.append(course[0])

        mute = 0
        if user in muted:
            mute = 1

        return page_view('alter-user', user=user, courses=uCourses, admin=admin, muted=mute)
    
#-----------------------------------------------------------------------------

def delUser(user):
    from run import manage_db
    sql_db = manage_db()

    sql_db.userDelete(user)

    return page_view('admin', name=user, users=sql_db.users(), courses=getCourses())

#-----------------------------------------------------------------------------

def mute(user, mute):
    if mute == 'Y':
        if user not in muted:
            muted.append(user)
    elif mute == 'Y':
        if user in muted:
            muted.remove(user)
    
    from run import manage_db
    sql_db = manage_db()

    uCourses = []
    for course in courses:
        if user in course[1]:
            uCourses.append(course[0])

    mute = 0
    if user in muted:
        mute = 1
    
    return page_view('alter-user', user=user, courses=uCourses, admin=sql_db.isAdmin(user), muted=mute)

#-----------------------------------------------------------------------------

def course_name(old, new):
    '''
        start_chat
        Starts chat
        Returns chat page
    '''

    found = 0
    i = 0
    while i < len(courses):
        if courses[i][0] == old:
            if new != "":
                courses[i][0] = new
            found = i
            break
        i += 1
    print("Renamed ", found, " Old ", old, " New ", new)

    return page_view("alter-course", course=courses[found][0], users=courses[found][1])

#-----------------------------------------------------------------------------

def course_delete(course, name):
    '''
        start_chat
        Starts chat
        Returns chat page
    '''

    for c in courses:
        if c[0] == course:
            courses.remove(c)
            break

    from run import manage_db
    sql_db = manage_db()

    return page_view("admin", name=name, users=sql_db.users(), courses=getCourses())

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

def getCourses(name='none'):
    uCourses = []
    for course in courses:
        if name == 'none' or name in course[1]:
            uCourses.append(course[0])
    return uCourses