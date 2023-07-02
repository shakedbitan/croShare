# written by Shaked Bitan
# all database methods
import sqlite3
db_path = r"C:\Users\Toshiba\database.db"


def create_connection(path):
    """creating connection to database"""
    connection = None
    cursor = None
    try:
        connection = sqlite3.connect(path)
        cursor = connection.cursor()
        print("Connection to SQLite DB was successful")
    except Exception as e:
        print("error occurred")
        print(e)
    return connection, cursor


def add_new_user(cursor, gmail, username, password, salt, manager=0):
    """add new user to data base"""
    cursor.execute("""INSERT INTO users (username,gmail,password,salt,manager) VALUES (?,?,?,?,?);""", (username, gmail, password, salt, manager))
    print("NEW USER ADDED")


def does_username_exists(cursor, username):
    """check if username exists"""
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    if cursor.fetchone() is not None:
        return True
    return False


def get_user_password_and_salt(cursor, username):
    """get the password and salt of a user"""
    cursor.execute('SELECT password,salt FROM users WHERE username = ?', (username, ))
    data = cursor.fetchone()
    if data is None:
        #username does not exist
        return ["0", "0"]
    return data


def is_user_manager(cursor,username):
    """check if user is manager, if so, return True"""
    cursor.execute("SELECT manager FROM users WHERE username = ?", (username,))
    data = cursor.fetchone()
    if data[0] == 0:
        return False
    return True


def upload_pattern_to_db(cursor, username, date, pattern_name, category, subcategory,d_level, p_object):
    """upload new pattern to server, including all attributes"""
    cursor.execute("""INSERT INTO patterns (username, date, "pattern name", category, subcategory,"difficulty level", "pattern object") VALUES (?,?,?,?,?,?,?);""", (username, date, pattern_name, category, subcategory,d_level, p_object))
    print("NEW PATTERN ADDED")


def start_new_pattern(cursor, username, pattern_name, rounds_done, date, time):
    """insert new line to patterns in progress"""
    username = username.strip()
    pattern_name = pattern_name.strip()
    cursor.execute("""INSERT INTO 'patterns in progress' (username, 'pattern name', 'rounds done', 'last date', 'time') VALUES (?,?, ?, ?, ?);""", (username, pattern_name, rounds_done, date, time))


def get_time_pattern(cursor, username, pattern_name):
    """get the current time in a pattern"""
    cursor.execute('SELECT time FROM "patterns in progress" WHERE username = ? AND "pattern name" = ?', (username, pattern_name,))
    time = cursor.fetchone()[0]
    return time


def update_pattern_in_progress(cursor, username, pattern_name, rounds_done, date, time):
    """update rounds done and date"""
    cursor.execute("""UPDATE 'patterns in progress' SET 'rounds done' = ?, 'last date' = ?, time = ? WHERE username = ? AND 'pattern name' = ?""", (rounds_done, date, username, pattern_name, time))


def get_pattern(cursor, pattern_name):
    """get pattern object from db. only need blob data"""
    cursor.execute('SELECT * FROM patterns WHERE "pattern name" = ?', (pattern_name,))
    data = cursor.fetchone()[-2]
    return data


def how_many_patterns(cursor):
    """count how many patterns are there in db"""
    cursor.execute("SELECT COUNT (*) FROM patterns")
    num = cursor.fetchone()[0]
    return num


def get_random_pattern(cursor):
    """get a random pattern from table. only need the blob data"""
    cursor.execute('SELECT "pattern object" FROM patterns ORDER BY RANDOM() LIMIT 1')
    random_pattern = cursor.fetchone()[0]
    return random_pattern


def was_pattern_started(cursor, username, pattern_name):
    """check if user started this pattern"""
    cursor.execute('SELECT * FROM "patterns in progress" WHERE username = ? AND "pattern name" = ?', (username, pattern_name,))
    if cursor.fetchone() is None:
        # it is the first time user wants to do this pattern
        return False
    return True


def get_rounds_done(cursor, username, pattern_name):
    cursor.execute('SELECT "rounds done" FROM "patterns in progress" WHERE username = ? AND "pattern name" =  ?', (username, pattern_name,))
    return cursor.fetchone()[0]


def want_to_be_managers(cursor):
    """create string of all users who wants to be managers"""
    cursor.execute("SELECT username FROM users WHERE manager = 2")
    rows = cursor.fetchall()
    future_managers = ""
    for row in rows:
        future_managers += row[0] + " "
    return future_managers


def pattern_done(cursor, username, pattern_name):
    """add pattern to records of pattern that were done."""
    # first we check if pattern was already done by user
    cursor.execute('SELECT * from "patterns done" WHERE username = ? AND "pattern name" = ?', (username, pattern_name,))
    if cursor.fetchone() is not None:
        # pattern was already done by user, so we just add 1 to times
        cursor.execute("""UPDATE "patterns done" SET times = times + 1 WHERE username = ? AND "pattern name" = ?""", (username, pattern_name))

    else:
        # we create a new row of pattern
        cursor.execute("""INSERT INTO "patterns done" (username, "pattern name", times) VALUES (?,?,?);""", (username, pattern_name, 1))


def users_patterns_in_progress(cursor, username):
    """get all the patterns in progress of a user"""
    cursor.execute('SELECT "pattern name" FROM "patterns in progress" WHERE username = ?',(username,))
    p_names = cursor.fetchall()
    names = ""
    for name in p_names:
        names+=name[0]+","
    return names


def users_uploads(cursor, username):
    """get all uplods user has uploaded"""
    cursor.execute('SELECT "pattern name" FROM patterns WHERE username = ?', (username,))
    p_names = cursor.fetchall()
    names = ""
    for name in p_names:
        names += name[0] + ","
    return names


def users_work(cursor, username):
    """get all users work from patterns done"""
    cursor.execute('SELECT "pattern name", times FROM "patterns done" WHERE username = ?', (username,))
    rows = cursor.fetchall()
    patterns_string = ""
    for row in rows:
        pattern_name, times = row
        patterns_string = str(pattern_name)+","+str(times)+"|"
    return patterns_string


def delete_row_from_patterns_in_progress(cursor, username, pattern_name):
    """deleting a row from database"""
    print("Deleting row for username:", username, "and pattern name:", pattern_name)
    cursor.execute("DELETE FROM `patterns in progress` WHERE username = ? AND `pattern name` = ?", (username, pattern_name))


def approve_user(cursor, username):
    """change manager column to 3"""
    cursor.execute("""UPDATE users SET manager = 3 WHERE username = ?""", (username,))


def disapprove_user(cursor, username):
    """change manager column to 4"""
    cursor.execute("""UPDATE users SET manager = 4 WHERE username = ?""", (username,))


def get_username_manager_state(cursor, username):
    """check what is in column manager. if 4- return 4 and turn it into 0, if 3- return 3 and turn it into 1"""
    cursor.execute("SELECT manager FROM users WHERE username = ?", (username,))
    manager_state = cursor.fetchone()[0]
    if manager_state == 0 or manager_state == 1:
        return 0
    elif manager_state == 3:
        # we update the state to be current
        cursor.execute("""UPDATE users SET manager = 1 WHERE username = ?""", (username,))
        return 3
    elif manager_state == 4:
        # we update the state to be current
        cursor.execute("""UPDATE users SET manager = 0 WHERE username = ?""", (username,))
        return 4


def manager_request(cursor, username):
    """change manager state into 2"""
    cursor.execute("""UPDATE users SET manager = 2 WHERE username = ?""", (username,))
    print("uploaded")


if __name__ == '__main__':
    conn, cursor = create_connection(db_path)
    conn.commit()
