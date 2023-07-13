'''
    This is a file that configures how your server runs
    You may eventually wish to have your own explicit config file
    that this reads from.

    For now this should be sufficient.

    Keep it clean and keep it simple, you're going to have
    Up to 5 people running around breaking this constantly
    If it's all in one file, then things are going to be hard to fix

    If in doubt, `import this`
'''

#-----------------------------------------------------------------------------

import os
import sys
import ssl

#-----------------------------------------------------------------------------
# You may eventually wish to put these in their own directories and then load 
# Each file separately

# For the template, we will keep them together

import model
import view
import controller

#-----------------------------------------------------------------------------

host = '0.0.0.0'
port = 443

# Turn this off for production
debug = True


def run_server():
    from bottle import run, app
    import bottle_session
    '''
        run_server
        Runs a bottle server
    '''

    certfile = "cert/INFO2222.crt"
    keyfile = "cert/INFO2222.key"

    app = app()
    plugin = bottle_session.SessionPlugin(cookie_lifetime=None)
    app.install(plugin)
    run(app=app, host=host, port=port, debug=debug, server='gunicorn', keyfile=keyfile, certfile=certfile)

#-----------------------------------------------------------------------------

database_args = "users.db"
import sql

def database_setup():
    '''
        database_setup
        Resets SQL databse for the server
    '''
    sql_db = sql.SQLDatabase(database_arg=database_args)
    sql_db.database_setup()
    
def manage_db():
    '''
        manage_db
        Starts up and re-initialises an SQL databse for the server
    '''
    # Currently runs in RAM, might want to change this to a file if you use it
    sql_db = sql.SQLDatabase(database_arg=database_args)

    return sql_db


#-----------------------------------------------------------------------------

# What commands can be run with this python file
# Add your own here as you see fit

command_list = {
    'manage_db' : manage_db,
    'database_setup' : database_setup,
    'server'       : run_server
}

# The default command if none other is given
default_commands = ['database_setup', 'server']

def run_commands(args):
    '''
        run_commands
        Parses arguments as commands and runs them if they match the command list

        :: args :: Command line arguments passed to this function
    '''
    commands = args[1:]

    # Default command
    if len(commands) == 0:
        commands = default_commands

    for command in commands:
        if command in command_list:
            command_list[command]()
        else:
            print("Command '{command}' not found".format(command=command))

#-----------------------------------------------------------------------------

if __name__ == "__main__":
    run_commands(sys.argv)