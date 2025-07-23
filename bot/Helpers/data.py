import sqlite3
from Helpers import constants,server

def get_connection():
    """
    Returns a connection to the SQLite database.
    This function can be used to connect to the database for executing queries.
    """
    conn = sqlite3.connect(constants.database_path)
    return conn,conn.cursor()

def close_connection(conn):
    """
    Closes the connection to the SQLite database.
    This function should be called after all database operations are complete.
    """
    if conn:
        conn.commit()
        conn.close()

def initialize_data():
    """
    Initializes the data for the application.
    This function can be used to set up any necessary data structures or variables.
    """
    conn,cursor = get_connection()
    
    cursor.execute("PRAGMA foreign_keys = ON;")
    
    cursor.execute("""CREATE TABLE IF NOT EXISTS guilds (guild_id INTEGER PRIMARY KEY);""")
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER NOT NULL,
        username TEXT NOT NULL UNIQUE,
        
        region INTEGER NOT NULL,
        empire TEXT DEFAULT 'None',
        claim TEXT DEFAULT 'None',
        
        carpentry INTEGER DEFAULT 1,
        mining INTEGER DEFAULT 1,
        fishing INTEGER DEFAULT 1,
        farming INTEGER DEFAULT 1,
        foraging INTEGER DEFAULT 1,
        forestry INTEGER DEFAULT 1,
        scholar INTEGER DEFAULT 1,
        masonry INTEGER DEFAULT 1,
        smithing INTEGER DEFAULT 1,
        tailoring INTEGER DEFAULT 1,
        hunting INTEGER DEFAULT 1,
        leatherworking INTEGER DEFAULT 1,
        
        construction INTEGER DEFAULT 1,
        cooking INTEGER DEFAULT 1,
        merchanting INTEGER DEFAULT 1,
        sailing INTEGER DEFAULT 1,
        slayer INTEGER DEFAULT 1,
        taming INTEGER DEFAULT 1,
        
        PRIMARY KEY (user_id)
    );""")
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS guild_settings (
        guild_id TEXT PRIMARY KEY,
        verification_enabled BOOLEAN DEFAULT FALSE,
        verification_type TEXT DEFAULT 'verified',
        verification_role INTEGER
        
        guild_empire TEXT DEFAULT 'None',
        guild_claim TEXT DEFAULT 'None'
    );""")
    
    # group_type: empire claim group
    cursor.execute("""CREATE TABLE IF NOT EXISTS groups (
        group_type TEXT NOT NULL, 
        owner_id INTEGER NOT NULL,
        name TEXT PRIMARY KEY,
        description TEXT,
        discord_id INTEGER,
        discord_link TEXT,
        region INTEGER NOT NULL,
        empire TEXT DEFAULT 'None',
        
        FOREIGN KEY (owner_id) REFERENCES users(user_id) ON DELETE CASCADE
    );""")
    
    cursor.execute("""CREATE TABLE IF NOT EXISTS verification_messages (
        guild_id INTEGER NOT NULL,
        message_id INTEGER NOT NULL,
        channel_id INTEGER NOT NULL,
        PRIMARY KEY (guild_id, message_id),
        FOREIGN KEY (guild_id) REFERENCES guilds(guild_id) ON DELETE CASCADE
    );""")
    
    close_connection(conn)

def update_database(username):
    """Updates from BitJita."""
    data = server.PlayerInformation(username)
    
    Update("users", {"username": username}, {
        "region": 3,
        "empire": data.empires[0],
        "claim": data.claims,
        
        **{skill.lower(): xp for skill, xp in data.skills.items()}
    }, update=True)

from discord.ext import commands
class InjectionError(commands.CommandError):
    pass

def injection_check(parameters:list):
    disabled_characters = ['"',"]","[","{","}"," OR ","="," AND "," WHERE "," DROP "," IS ",";","%"]
    for char in disabled_characters:
        if any(str(char.lower()) in str(s).lower() for s in parameters):
            raise InjectionError()
        
def command_line(string:str):
    conn,cursor = get_connection()
    
    print(string)
    cursor.execute(string)
    
    close_connection(conn)

def Update(database:str, _where:dict={}, _set:dict={}, _values:dict={}, *, update:bool=True, delete_empty:tuple[bool,str]=False):
    """Edit an entry in a database given arguments.

    Args:
        database(str): The database you are writing to.
        _where(dict<str,var>): A dictionary of database keys and values to filter by.
        _set(dict<str,var>): A dictionary of database keys and values to set.
        
        (optional) update(bool): If False, always creates a new entry instead of updating an existing one.
        (optional) delete_empty(tuple[bool,str]): If True, deletes entry if column str goes negative. 
    
    Returns:
        bool: True if successful, False if false 
    """
    conn,cursor = get_connection()
    injection_check(list(_where.values()) + list(_set.values()) + list(_values.values()) if _values else [])
    
    _values = _where.copy()
    _values.update(_values)
    _values.update(_set)
    
    wherestr = ""
    for key in _where:
        if type(_where[key]) is tuple:
            wherestr += f'{key} {_where[key][0]} AND '
        else: wherestr += f'{key} = ? AND '
    wherestr = wherestr[:-4]
    if constants.debug:print(f"SELECT * FROM {database} WHERE "+wherestr,list(_where.values()))
    cursor.execute(f"SELECT * FROM {database} WHERE "+wherestr,list(_where.values()))
    exists = cursor.fetchall()

    try:
        if len(exists) > 0 and update:   
            columns = [desc[0] for desc in cursor.description]
            data = [dict(zip(columns, row)) for row in exists]
            
            for key,value in _set.items():
                if type(value) is tuple:
                    if value[1] == "+":
                        _set[key] = value[0] + data[0][key]
                        if constants.debug:print("DEBUG: "+str(_set[key]))
                        if constants.debug:print("DEBUG: "+str(not delete_empty == None))
                        if constants.debug and delete_empty: print("DEBUG: "+str(key==delete_empty[1]))
                        if delete_empty and key == delete_empty[1] and _set[key] <= 0:
                            print("Deleting empty entry.")
                            cursor.execute(f'DELETE FROM {database} WHERE '+wherestr,list(_where.values()))
                            conn.commit()
                            conn.close()
                            conn = None
                            return True, -_set[key]
                
            setstr = ""
            for key in _set:
                setstr += f'{key} = ?,'
            setstr = setstr[:-1]
            
            cursor.execute(f'UPDATE {database} SET {setstr} WHERE {wherestr}', list(_set.values()) + list(_where.values()))
            return True, None
        else:
            for key,value in _values.items():
                if type(value) is tuple:
                    if value[1] == "+":
                        _values[key] = value[0]
                        if delete_empty and key == delete_empty[1] and _values[key] <= 0:
                            print("Nullifying empty entry.")
                            conn.commit()
                            conn.close()
                            conn = None
                            return False, None
                            
            valuelen = []
            
            for _ in _values.keys():
                valuelen.append("?")
            
            if constants.debug: print(f'INSERT INTO {database} ({", ".join(list(_values.keys()))}) VALUES ({",".join(valuelen)})', list(_values.values()))
            cursor.execute(f'INSERT INTO {database} ({", ".join(list(_values.keys()))}) VALUES ({",".join(valuelen)})', list(_values.values()))
            return True, None
    except sqlite3.OperationalError as e:
        print(f"An error occurred: {e}")
        return False, None
    finally:
        if conn: close_connection(conn)

def Get(database:str, _where:dict={}):
    """Get an entry in a database given arguments.

    Args:
        database(str): The database you are writing to.
        _where(dict<str,var>): A dictionary of database keys and values to filter by.
    
    Returns:
        data: Fetched data
    """
    conn,cursor = get_connection()
    
    if _where == {}:
        if constants.debug: print(f"SELECT * FROM {database}")
        cursor.execute(f"SELECT * FROM {database}")
        all = cursor.fetchall()
        
        columns = [desc[0] for desc in cursor.description]
        data = [dict(zip(columns, row)) for row in all]
        
        close_connection(conn)
        return data
    
    wherestr = ""
    delkeys = []
    for key in _where:
        if type(_where[key]) is tuple:
            wherestr += f'{key} {_where[key][0]} AND '
            delkeys.append(key)
        else: wherestr += f'{key} = ? AND '
    for key in delkeys:
        del _where[key]
    wherestr = wherestr[:-4]
    if constants.debug: print(f"SELECT * FROM {database} WHERE "+wherestr,list(_where.values()))
    cursor.execute(f"SELECT * FROM {database} WHERE "+wherestr,list(_where.values()))
    all = cursor.fetchall()
    
    columns = [desc[0] for desc in cursor.description]
    data = [dict(zip(columns, row)) for row in all]
    
    close_connection(conn)
    return data

def Remove(database:str, _where:dict={}):
    """Remove an entry in a database given arguments.

    Args:
        database(str): The database you are writing to.
        _where(dict<str,var>): A dictionary of database keys and values to filter by.
    
    Returns:
        bool: True if successful, False if false 
    """
    conn,cursor = get_connection()
    injection_check(list(_where.values()))
    
    wherestr = ""
    for key in _where:
        if type(_where[key]) is tuple:
            wherestr += f'{key} {_where[key][0]} AND '
        else: wherestr += f'{key} = ? AND '
    wherestr = wherestr[:-4]
    
    if constants.debug: print(f"DELETE FROM {database} WHERE "+wherestr,list(_where.values()))
    cursor.execute(f"DELETE FROM {database} WHERE "+wherestr,list(_where.values()))
    
    close_connection(conn)
    return True

def GetOne(database:str, _where:dict={}):
    results = Get(database, _where)
    if len(results) == 0:
        return None
    elif len(results) == 1:
        return results[0]