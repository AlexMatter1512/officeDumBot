# todo_util.py
import dotenv
import os
import sqlite3
from pathlib import Path

dotenv.load_dotenv()
DB_PATH = os.getenv('DB_FILE_PATH', './todo.db')

def _get_connection():
    """Get a connection to the SQLite database."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Allow accessing columns by name
    return conn

def _ensure_list_table(list_name: str):
    """Create a table for the specified list if it doesn't exist."""
    conn = _get_connection()
    cursor = conn.cursor()
    
    # Create a table for this specific list
    # SQLite doesn't allow parameterized table names, need to sanitize manually
    table_name = f"list_{list_name.replace(' ', '_').lower()}"
    
    # Check if the table exists
    cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
    if not cursor.fetchone():
        cursor.execute(f'''
        CREATE TABLE {table_name} (
            id INTEGER PRIMARY KEY,
            content TEXT NOT NULL
        )
        ''')
        conn.commit()
    
    conn.close()
    return table_name

def add_item(todo_item: str, list: str = "todo"):
    """Append a list item to the database."""
    table_name = _ensure_list_table(list)
    
    conn = _get_connection()
    cursor = conn.cursor()
    
    # Insert the new item
    cursor.execute(f"INSERT INTO {table_name} (content) VALUES (?)", (todo_item,))
    conn.commit()
    conn.close()

def get_all_items(list: str = "todo"):
    """Retrieve all list items from the database."""
    table_name = _ensure_list_table(list)
    
    conn = _get_connection()
    cursor = conn.cursor()
    
    # Get all items for the specified list
    cursor.execute(f"SELECT content FROM {table_name}")
    items = [item[0] + '\n' for item in cursor.fetchall()]
    conn.close()
    
    return items

def remove_item_by_index(index: int, list: str = "todo"):
    """Remove a list item by its index."""
    table_name = _ensure_list_table(list)
    
    conn = _get_connection()
    cursor = conn.cursor()
    
    # Get all items for the list
    cursor.execute(f"SELECT id, content FROM {table_name} ORDER BY id")
    db_items = cursor.fetchall()
    
    if index < 0 or index >= len(db_items):
        conn.close()
        return None
    
    removed_item = db_items[index]['content'].strip()
    
    # Delete the item at the specified index
    cursor.execute(f"DELETE FROM {table_name} WHERE id=?", (db_items[index]['id'],))
    conn.commit()
    conn.close()
    
    return removed_item
