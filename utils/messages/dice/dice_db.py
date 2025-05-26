import sqlite3
import os
from typing import List
import dotenv
from datetime import date
from var.messages.dice.slot import Game
import logging
from enum import StrEnum

log = logging.getLogger("dice_db")
dotenv.load_dotenv()

## DATA
DB_FILE_PATH = os.getenv('DB_FILE_PATH', './db.db')
TABLE_NAME = 'dice'

class Entry(StrEnum):
    ID = 'id'
    USER_ID = 'user_id'
    DATE = 'date'
    GAME = 'game'
    ATTEMPT = 'attempt'
    WON = 'won'

os.makedirs(os.path.dirname(DB_FILE_PATH), exist_ok=True)

#init db on module import
def init_db():
    conn = sqlite3.connect(DB_FILE_PATH)
    cursor = conn.cursor()
    
    cursor.execute(f'''
    CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
        {Entry.ID} INTEGER PRIMARY KEY AUTOINCREMENT,
        {Entry.USER_ID} TEXT NOT NULL,
        {Entry.DATE} DATE NOT NULL,
        {Entry.GAME} TEXT NOT NULL,
        {Entry.ATTEMPT} TEXT NOT NULL,
        {Entry.WON} INTEGER NOT NULL
    )
    ''')
    
    conn.commit()
    conn.close()

init_db()

## DB ACCESS
def get_monthly_wins(user: str, month: int, year: int) -> int:
    conn = sqlite3.connect(DB_FILE_PATH)
    cursor = conn.cursor()
    
    cursor.execute(f'''
    SELECT COUNT(*) FROM {TABLE_NAME}
    WHERE {Entry.USER_ID} = ? 
    AND strftime('%Y-%m', {Entry.DATE}) = ? 
    AND {Entry.WON} = 1
    ''', (user, f"{year}-{month:02}"))
    
    wins = cursor.fetchone()[0]
    conn.close()
    
    return wins

def get_all_monthly_wins(month: int, year: int) -> dict:
    conn = sqlite3.connect(DB_FILE_PATH)
    cursor = conn.cursor()
    
    cursor.execute(f'''
    SELECT {Entry.USER_ID}, COUNT(*) FROM {TABLE_NAME}
    WHERE strftime('%Y-%m', {Entry.DATE}) = ? AND {Entry.WON} = 1
    GROUP BY {Entry.USER_ID}
    ''', (f"{year}-{month:02}",))
    
    wins = {user: count for user, count in cursor.fetchall()}
    conn.close()
    
    return wins

def get_all_monthly_players(month: int, year: int) -> List[str]:
    """
    Get all players who have played in the given month and year.
    """
    conn = sqlite3.connect(DB_FILE_PATH)
    cursor = conn.cursor()
    
    cursor.execute(f'''
    SELECT DISTINCT {Entry.USER_ID} FROM {TABLE_NAME}
    WHERE strftime('%Y-%m', {Entry.DATE}) = ?
    ''', (f"{year}-{month:02}",))
    
    players = [user[0] for user in cursor.fetchall()]
    conn.close()
    
    return players

def get_daily_attempts_count(user: str, game: Game) -> int:
    """
    Get the number of attempts the user has made today for the given game.
    """
    conn = sqlite3.connect(DB_FILE_PATH)
    cursor = conn.cursor()
    
    cursor.execute(f'''
    SELECT COUNT(*) FROM {TABLE_NAME}
    WHERE {Entry.USER_ID} = ? AND {Entry.DATE} = ? AND {Entry.GAME} = ?
    ''', (user, date.today(), game))
    
    count = cursor.fetchone()[0]
    conn.close()
    
    return count

def get_daily_games_count(user: str) -> int:
    """
    Get the number of distinct games the user has played today.
    """
    conn = sqlite3.connect(DB_FILE_PATH)
    cursor = conn.cursor()
    
    cursor.execute(f'''
    SELECT COUNT(DISTINCT {Entry.GAME}) FROM {TABLE_NAME}
    WHERE {Entry.USER_ID} = ? AND {Entry.DATE} = ?
    ''', (user, date.today()))
    
    count = cursor.fetchone()[0]
    conn.close()
    
    return count

def get_daily_attempts(user: str, game: Game) -> List[int]:
    """
    Get the user's attempts for the given game today.
    """
    conn = sqlite3.connect(DB_FILE_PATH)
    cursor = conn.cursor()
    
    cursor.execute(f'''
    SELECT {Entry.ATTEMPT} FROM {TABLE_NAME}
    WHERE {Entry.USER_ID} = ? AND {Entry.DATE} = ? AND {Entry.GAME} = ?
    ''', (user, date.today(), game))

    attempts = [int(attempt[0]) for attempt in cursor.fetchall()]
    conn.close()

    return attempts

def add_daily_game_attempt(user: str, game: Game, attempt: str, won: bool):
    """
    Add a new game attempt to the database.
    Each attempt is stored as a separate row.
    """
    conn = sqlite3.connect(DB_FILE_PATH)
    cursor = conn.cursor()
    
    # Simply insert a new row for the attempt
    cursor.execute(f'''
    INSERT INTO {TABLE_NAME} ({Entry.USER_ID}, {Entry.DATE}, {Entry.GAME}, {Entry.ATTEMPT}, {Entry.WON})
    VALUES (?, ?, ?, ?, ?)
    ''', (user, date.today(), game, attempt, 1 if won else 0))
    
    conn.commit()
    conn.close()
