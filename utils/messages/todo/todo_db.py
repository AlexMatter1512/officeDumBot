import os
import sqlite3
import logging
import textwrap
import dotenv
from enum import StrEnum, auto


class TodoItem:
    class Label(StrEnum):
        ID = "id"
        USER_ID = "user_id"
        TEXT = "todo_text"
        DATE = "insert_date"
        UPDATE_DATE = "update_date"
        STATUS = "status"
        PRIORITY = "priority"
        NETWORK = "network"
        _message_id = "message_id"
        _deleted = "deleted"

    class Status(StrEnum):
        ACTIVE = "active"
        DONE = "done"

    class Priority(StrEnum):
        LOW = "low"
        NORMAL = "normal"
        HIGH = "high"

    def __init__(
        self,
        user_id: str,
        text: str,
        status: str = Status.ACTIVE,
        priority: str = Priority.NORMAL,
        deleted: bool = False,
        update_date: str = None,
        date: str = None,
        message_id: int = None,
        network: str = None,
        db_id: int = None,
    ):
        self.id = db_id
        self.user_id = user_id
        self.text = text
        self.status = status
        self.priority = priority
        self.message_id = message_id
        self.deleted = deleted
        self.network = network
        self.date = date  # This will be set when the item is added to the database
        self.update_date = update_date  # This will be set when the item is updated in the database

    def __repr__(self):
        # Priority emojis
        priority_emoji = {
            self.Priority.LOW: "🟢",
            self.Priority.NORMAL: "🟡",
            self.Priority.HIGH: "🔴",
        }.get(self.priority, "")

        # Status emojis
        status_emoji = {
            self.Status.ACTIVE: "⏳",
            self.Status.DONE: "✅",
        }.get(self.status, "")

        # Create main text part
        string = textwrap.dedent(
            f"""
            TODO:
            ```
            {self.text}
            ```
            ID: {self.id}
            Priority: {priority_emoji} {self.priority}
            Status: {status_emoji} {self.status}
            Added by: {self.user_id}
            """
        )

        if self.date:
            string += f"Added on: {self.date}\n"

        if self.update_date:
            string += f"Updated on: {self.update_date}\n"

        if self.network:
            string += f"Network: {self.network}"

        if self.message_id:
            string += f"Message ID: {self.message_id}"

        return string


log = logging.getLogger("todo_db")
dotenv.load_dotenv()

## DATA
DB_FILE_PATH = os.getenv("DB_FILE_PATH", "./db.db")
TABLE_NAME = "todo_v2"
os.makedirs(os.path.dirname(DB_FILE_PATH), exist_ok=True)


# init db on module import
def init_db():
    conn = sqlite3.connect(DB_FILE_PATH)
    cursor = conn.cursor()

    cursor.execute(
        f"""
    CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
        {TodoItem.Label.ID} INTEGER PRIMARY KEY AUTOINCREMENT,
        {TodoItem.Label.USER_ID} TEXT NOT NULL,
        {TodoItem.Label._message_id} INTEGER UNIQUE,
        {TodoItem.Label._deleted} INTEGER DEFAULT 0,
        {TodoItem.Label.TEXT} TEXT NOT NULL,
        {TodoItem.Label.DATE} DATE DEFAULT (datetime('now', 'localtime') ),
        {TodoItem.Label.UPDATE_DATE} DATE DEFAULT (datetime('now', 'localtime') ),
        {TodoItem.Label.STATUS} TEXT DEFAULT 'active',
        {TodoItem.Label.PRIORITY} TEXT DEFAULT 'normal',
        {TodoItem.Label.NETWORK} TEXT DEFAULT 'telegram'
    )
    """
    )

    conn.commit()
    conn.close()


init_db()

## DB ACCESS


def get_todo_item(id: int) -> TodoItem:
    """Get a todo item from the database by its ID."""
    conn = sqlite3.connect(DB_FILE_PATH)
    cursor = conn.cursor()

    cursor.execute(
        f"""
        SELECT {TodoItem.Label.ID}, {TodoItem.Label.USER_ID}, {TodoItem.Label.TEXT},
               {TodoItem.Label.DATE}, {TodoItem.Label.STATUS}, {TodoItem.Label.PRIORITY},
               {TodoItem.Label.NETWORK}, {TodoItem.Label.UPDATE_DATE}
        FROM {TABLE_NAME}
        WHERE {TodoItem.Label.ID} = ?
        """,
        (id,),
    )
    row = cursor.fetchone()
    conn.close()

    if row:
        todo_item = TodoItem(
            user_id=row[1],
            text=row[2],
            status=row[4],
            priority=row[5],
            network=row[6],
            update_date=row[7],
            db_id=row[0],
        )
        todo_item.date = row[3]
        return todo_item
    else:
        return None
    
def get_todo_item_by_message_id(message_id: int) -> TodoItem:
    """Get a todo item from the database by its message ID."""
    conn = sqlite3.connect(DB_FILE_PATH)
    cursor = conn.cursor()

    cursor.execute(
        f"""
        SELECT {TodoItem.Label.ID}, {TodoItem.Label.USER_ID}, {TodoItem.Label.TEXT},
               {TodoItem.Label.DATE}, {TodoItem.Label.STATUS}, {TodoItem.Label.PRIORITY},
               {TodoItem.Label.NETWORK}
        FROM {TABLE_NAME}
        WHERE {TodoItem.Label._message_id} = ?
        """,
        (message_id,),
    )
    row = cursor.fetchone()
    conn.close()

    if row:
        todo_item = TodoItem(
            user_id=row[1],
            text=row[2],
            status=row[4],
            priority=row[5],
            network=row[6],
            db_id=row[0],
        )
        todo_item.date = row[3]
        return todo_item
    else:
        return None


def add_todo_item_full(
    user_id: str,
    text: str,
    status: str = "active",
    priority: str = "normal",
    network: str = None,
) -> TodoItem:
    """Add a new todo item to the database."""
    conn = sqlite3.connect(DB_FILE_PATH)
    cursor = conn.cursor()

    try:
        cursor.execute(
            f"""
        INSERT INTO {TABLE_NAME} (
            {TodoItem.Label.USER_ID},
            {TodoItem.Label.TEXT},
            {TodoItem.Label.STATUS},
            {TodoItem.Label.PRIORITY},
            {TodoItem.Label.NETWORK}
        ) VALUES (?, ?, ?, ?, ?)
        """,
            (user_id, text, status, priority, network),
        )
        conn.commit()
        todo_id = cursor.lastrowid

        log.info(f"Todo item added with ID: {todo_id}")
    except sqlite3.Error as e:
        log.error(f"Error adding todo item: {e}")
        conn.rollback()
        return None
    finally:
        conn.close()
    todo_item = get_todo_item(todo_id)
    if not todo_item:
        log.error(f"Failed to retrieve the added todo item with ID: {todo_id}")
        return None
    return todo_item


def add_todo_item(todoItem: TodoItem) -> TodoItem:
    return add_todo_item_full(
        user_id=todoItem.user_id,
        text=todoItem.text,
        status=todoItem.status,
        priority=todoItem.priority,
        network=todoItem.network,
    )


def get_todo_items(
    user_id: str, status: str = "active", priority: str = None, network: str = None
) -> list[TodoItem]:
    """Get todo items from the database."""
    conn = sqlite3.connect(DB_FILE_PATH)
    cursor = conn.cursor()

    query = f"""
        SELECT {TodoItem.Label.ID}, {TodoItem.Label.USER_ID}, {TodoItem.Label.TEXT},
               {TodoItem.Label.DATE}, {TodoItem.Label.STATUS}, {TodoItem.Label.PRIORITY},
               {TodoItem.Label.NETWORK}
        FROM {TABLE_NAME}
        WHERE {TodoItem.Label.USER_ID} = ?
        AND {TodoItem.Label.STATUS} = ?
    """
    params = [user_id, status]

    if priority:
        query += f" AND {TodoItem.Label.PRIORITY} = ?"
        params.append(priority)

    if network:
        query += f" AND {TodoItem.Label.NETWORK} = ?"
        params.append(network)

    cursor.execute(query, tuple(params))
    rows = cursor.fetchall()
    conn.close()

    return [
        TodoItem(
            user_id=row[1],
            text=row[2],
            status=row[4],
            priority=row[5],
            network=row[6],
        )
        for row in rows
    ]

def set_todo_item_priority(
    id: int, priority: str
) -> TodoItem:
    """Set the priority of a todo item."""
    conn = sqlite3.connect(DB_FILE_PATH)
    cursor = conn.cursor()

    cursor.execute(
        f"""
        UPDATE {TABLE_NAME}
        SET {TodoItem.Label.PRIORITY} = ?,
            {TodoItem.Label.UPDATE_DATE} = (datetime('now', 'localtime'))
        WHERE {TodoItem.Label.ID} = ?
        """,
        (priority, id),
    )
    conn.commit()
    conn.close()

    return get_todo_item(id)

def set_todo_item_status(
    id: int, status: str
) -> TodoItem:
    """Set the status of a todo item."""
    conn = sqlite3.connect(DB_FILE_PATH)
    cursor = conn.cursor()

    cursor.execute(
        f"""
        UPDATE {TABLE_NAME}
        SET {TodoItem.Label.STATUS} = ? ,
            {TodoItem.Label.UPDATE_DATE} = (datetime('now', 'localtime'))
        WHERE {TodoItem.Label.ID} = ?
        """,
        (status, id),
    )
    conn.commit()
    conn.close()

    return get_todo_item(id)

def set_todo_item_network(
    id: int, network: str
) -> TodoItem:
    """Set the network of a todo item."""
    conn = sqlite3.connect(DB_FILE_PATH)
    cursor = conn.cursor()

    cursor.execute(
        f"""
        UPDATE {TABLE_NAME}
        SET {TodoItem.Label.NETWORK} = ?,
            {TodoItem.Label.UPDATE_DATE} = (datetime('now', 'localtime'))
        WHERE {TodoItem.Label.ID} = ?
        """,
        (network, id),
    )
    conn.commit()
    conn.close()

    return get_todo_item(id)


def set_todo_item_message_id(
    id: int, message_id: int
) -> TodoItem:
    """Set the message ID of a todo item."""
    conn = sqlite3.connect(DB_FILE_PATH)
    cursor = conn.cursor()

    cursor.execute(
        f"""
        UPDATE {TABLE_NAME}
        SET {TodoItem.Label._message_id} = ?
        WHERE {TodoItem.Label.ID} = ?
        """,
        (message_id, id),
    )
    conn.commit()
    conn.close()

    return get_todo_item(id)
    