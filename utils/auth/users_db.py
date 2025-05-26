# this file was unproudly vibe coded 
import os
import sqlite3
import logging
import dotenv
from enum import Enum, StrEnum, auto

log = logging.getLogger("users_db")
dotenv.load_dotenv()

## DATA
DB_FILE_PATH = os.getenv('DB_FILE_PATH', './db.db')
TABLE_NAME = 'users'
os.makedirs(os.path.dirname(DB_FILE_PATH), exist_ok=True)

class User(StrEnum):
    ID = 'id'
    USER_ID = 'user_id'
    USERNAME = 'username'
    FIRST_NAME = 'first_name'
    LAST_NAME = 'last_name'
    LANGUAGE_CODE = 'language_code'
    IS_ADMIN = 'is_admin'
    DATE = 'insert_date'

class UserDbCodes(Enum):
    SUCCESS = auto()

    USER_NOT_FOUND = auto()
    USER_ALREADY_EXISTS = auto()
    USER_NOT_ADMIN = auto()
    GENERIC_ERROR = auto()

#init db on module import
def init_db():
    conn = sqlite3.connect(DB_FILE_PATH)
    cursor = conn.cursor()
    
    cursor.execute(f'''
    CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
        {User.ID} INTEGER PRIMARY KEY AUTOINCREMENT,
        {User.USER_ID} TEXT NOT NULL UNIQUE,
        {User.USERNAME} TEXT,
        {User.FIRST_NAME} TEXT,
        {User.LAST_NAME} TEXT,
        {User.LANGUAGE_CODE} TEXT,
        {User.IS_ADMIN} INTEGER DEFAULT 0,
        {User.DATE} DATE DEFAULT (datetime('now', 'localtime') )
    )
    ''')
    
    conn.commit()
    conn.close()

init_db()

## DB ACCESS
def is_allowed_user(user_id: str) -> bool:
    """Check if the user id is found in the database."""
    conn = sqlite3.connect(DB_FILE_PATH)
    cursor = conn.cursor()
    
    cursor.execute(f'''
    SELECT {User.USER_ID} FROM {TABLE_NAME}
    WHERE {User.USER_ID} = ?
    ''', (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result is not None

def get_user_by_id(user_id: str) -> dict:
    conn = sqlite3.connect(DB_FILE_PATH)
    cursor = conn.cursor()
    
    cursor.execute(f'''
    SELECT * FROM {TABLE_NAME}
    WHERE {User.USER_ID} = ?
    ''', (user_id,))
    
    user = cursor.fetchone()
    conn.close()
    
    if user:
        return {
            User.ID: user[0],
            User.USER_ID: user[1],
            User.USERNAME: user[2],
            User.FIRST_NAME: user[3],
            User.LAST_NAME: user[4],
            User.LANGUAGE_CODE: user[5],
            User.IS_ADMIN: bool(user[6]),
            User.DATE: user[7]
        }
    return {}

def is_admin(user_id: str) -> bool:
    """Check if the user is an admin."""
    conn = sqlite3.connect(DB_FILE_PATH)
    cursor = conn.cursor()
    
    cursor.execute(f'''
    SELECT {User.IS_ADMIN} FROM {TABLE_NAME}
    WHERE {User.USER_ID} = ?
    ''', (user_id,))
    
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return bool(result[0])
    return False

def insert_new_user(user_id: str, username: str, first_name: str, last_name: str, language_code: str | None = None, is_admin: bool = False) -> int:
    conn = sqlite3.connect(DB_FILE_PATH)
    cursor = conn.cursor()

    if get_user_by_id(user_id) != {}:
        log.debug(f"User {user_id} already exists in the database.")
        return UserDbCodes.USER_ALREADY_EXISTS.value
    
    try:
        cursor.execute(f'''
        INSERT INTO {TABLE_NAME} ({User.USER_ID}, {User.USERNAME}, {User.FIRST_NAME}, {User.LAST_NAME}, {User.LANGUAGE_CODE}, {User.IS_ADMIN})
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, username, first_name, last_name, language_code, int(is_admin)))
        conn.commit()
        conn.close()
    except Exception as e:
        log.error(f"Error inserting user: {e}")
        conn.close()
        return UserDbCodes.GENERIC_ERROR.value
    
    return UserDbCodes.SUCCESS.value

def update_user(user_id: str, username: str | None = None, first_name: str | None = None, last_name: str | None = None, language_code: str | None = None, is_admin: bool | None = None) -> dict:
    conn = sqlite3.connect(DB_FILE_PATH)
    cursor = conn.cursor()
    
    updates = []
    params = []
    
    if username:
        updates.append(f"{User.USERNAME} = ?")
        params.append(username)
    if first_name:
        updates.append(f"{User.FIRST_NAME} = ?")
        params.append(first_name)
    if last_name:
        updates.append(f"{User.LAST_NAME} = ?")
        params.append(last_name)
    if language_code:
        updates.append(f"{User.LANGUAGE_CODE} = ?")
        params.append(language_code)
    if is_admin is not None:
        updates.append(f"{User.IS_ADMIN} = ?")
        params.append(int(is_admin))
    
    params.append(user_id)
    
    cursor.execute(f'''
    UPDATE {TABLE_NAME}
    SET {', '.join(updates)}
    WHERE {User.USER_ID} = ?
    ''', tuple(params))
    
    conn.commit()
    conn.close()
    
    return get_user_by_id(user_id)

def set_user_admin(user_id: str, is_admin: bool) -> dict:
    conn = sqlite3.connect(DB_FILE_PATH)
    cursor = conn.cursor()
    
    cursor.execute(f'''
    UPDATE {TABLE_NAME}
    SET {User.IS_ADMIN} = ?
    WHERE {User.USER_ID} = ?
    ''', (int(is_admin), user_id))
    
    conn.commit()
    conn.close()
    
    return get_user_by_id(user_id)

def delete_user(user_id: str) -> bool:
    conn = sqlite3.connect(DB_FILE_PATH)
    cursor = conn.cursor()
    
    cursor.execute(f'''
    DELETE FROM {TABLE_NAME}
    WHERE {User.USER_ID} = ?
    ''', (user_id,))
    
    conn.commit()
    conn.close()
    
    return cursor.rowcount > 0

def get_all_users() -> list:
    conn = sqlite3.connect(DB_FILE_PATH)
    cursor = conn.cursor()
    
    cursor.execute(f'''
    SELECT * FROM {TABLE_NAME}
    ''')
    
    users = cursor.fetchall()
    conn.close()
    
    return [
        {
            User.ID: user[0],
            User.USER_ID: user[1],
            User.USERNAME: user[2],
            User.FIRST_NAME: user[3],
            User.LAST_NAME: user[4],
            User.LANGUAGE_CODE: user[5],
            User.IS_ADMIN: bool(user[6]),
            User.DATE: user[7]
        }
        for user in users
    ]

def get_admins() -> list:
    conn = sqlite3.connect(DB_FILE_PATH)
    cursor = conn.cursor()
    
    cursor.execute(f'''
    SELECT * FROM {TABLE_NAME}
    WHERE {User.IS_ADMIN} = 1
    ''')
    
    admins = cursor.fetchall()
    conn.close()
    
    return [
        {
            User.ID: admin[0],
            User.USER_ID: admin[1],
            User.USERNAME: admin[2],
            User.FIRST_NAME: admin[3],
            User.LAST_NAME: admin[4],
            User.LANGUAGE_CODE: admin[5],
            User.IS_ADMIN: bool(admin[6]),
            User.DATE: admin[7]
        }
        for admin in admins
    ]

def get_user_count() -> int:
    conn = sqlite3.connect(DB_FILE_PATH)
    cursor = conn.cursor()
    
    cursor.execute(f'''
    SELECT COUNT(*) FROM {TABLE_NAME}
    ''')
    
    count = cursor.fetchone()[0]
    conn.close()
    
    return count
