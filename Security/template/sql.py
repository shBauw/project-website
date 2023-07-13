import sqlite3

class SQLDatabase():
    '''
        Our SQL Database

    '''

    # Get the database running
    def __init__(self, database_arg=":memory:"):
        self.conn = sqlite3.connect(database_arg)
        self.cur = self.conn.cursor()

    def execute(self, sql_string):
        out = None
        for string in sql_string.split(";"):
            try:
                out = self.cur.execute(string)
            except:
                pass
        return out

    # Commit changes to the database
    def commit(self):
        self.conn.commit()

    #-----------------------------------------------------------------------------
    
    # Sets up the database
    # Default admin password
    def database_setup(self, admin_password='admin'):

        # Clear the database if needed
        self.execute("DROP TABLE IF EXISTS Users")
        self.commit()

        # Create the users table
        self.execute("""CREATE TABLE Users(
            Id VARBINARY,
            username TEXT,
            password TEXT,
            admin INTEGER DEFAULT 0
        )""")

        self.commit()

        # Add our admin user
        # self.add_user('admin', admin_password, admin=1)

    #-----------------------------------------------------------------------------
    # User handling
    #-----------------------------------------------------------------------------

    # Add a user to the database
    def add_user(self, username, password, admin=0):
        sql_cmd = """
                INSERT INTO Users(Id, username, password, admin)
                VALUES({id}, '{username}', '{password}', {admin})
            """

        sql_cmd = sql_cmd.format(id=0, username=username, password=password, admin=admin)

        self.execute(sql_cmd)
        self.commit()
        return True

    #-----------------------------------------------------------------------------

    # Check login credentials
    def check_credentials(self, username, password):
        sql_query = """
                SELECT 1 
                FROM Users
                WHERE username = '{username}' AND password = '{password}'
            """

        sql_query = sql_query.format(username=username, password=password)

        self.execute(sql_query)

        # If our query returns
        if self.cur.fetchone():
            return True
        else:
            return False
        
    #-----------------------------------------------------------------------------

    # Return list of users
    def users(self):
        sql_query = """
            SELECT *
            FROM Users
        """

        self.execute(sql_query)

        tuples = self.cur.fetchall()

        users = []

        for row in tuples:
            users.append(row[1])

        return users;

    #-----------------------------------------------------------------------------
    # Methods below are deprecated (I believe)
    #-----------------------------------------------------------------------------

    # Set user id (cookie)
    def setUserID(self, user, cookie):
        sql_query = """
            UPDATE Users
            SET Id = '{cookie}'
            WHERE username = '{username}'
        """

        sql_query=sql_query.format(cookie=cookie, username=user)

        self.execute(sql_query)

        return 1
    
    #-----------------------------------------------------------------------------

    # Get user id (cookie)
    def getUserID(self, user):
        sql_query = """
            SELECT 1
            FROM Users
            WHERE username = '{username}'
        """

        sql_query=sql_query.format(username=user)

        self.execute(sql_query)

        return self.cur.fetchone()

