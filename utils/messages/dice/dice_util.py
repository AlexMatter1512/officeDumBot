from enum import Enum, auto
import dotenv
import os
import yaml
import logging
from telegram import Dice
from datetime import date
from typing import Callable, Dict, List, Tuple

# MAX_MONTHLY_WINS = 1
MAX_MONTHLY_WINS = None
MAX_GAMES_PER_DAY = 2


"""
sample yaml file:
user1:
    2021:
        10:
            01: 
                slot: [1, 2]
                dice: [4, 6]
                won: True
            02:
                slot: [5]
                dice: [1]
                won: False
            ...
"""
# UserAttempts = Dict[str, Dict[str, Dict[str, List[int]]]]
UserAttempts = Dict[str, Dict[str, Dict[str, Dict[str, Dict[str, List[int]]]]]]

log = logging.getLogger("dice")
dotenv.load_dotenv()
DICE_FILE_PATH = os.getenv('DICE_FILE_PATH', './dice.yaml')
# Ensure the directory exists
os.makedirs(os.path.dirname(DICE_FILE_PATH), exist_ok=True)

class RESULT_CODES(Enum):
    """Error codes for the dice game."""
    # for all games
    LOST = auto() # when the user has lost the game 
    WON = auto() # when the user has won the game 
    LAST_ATTEMPT = auto() # when the user has one attempt left 
    ALREADY_PLAYED = auto() # when the user has already played daily_attempts times
    ALREADY_PLAYED_GAMES = auto() # when the user has already played MAX_GAMES_PER_DAY games
    ALREADY_WON = auto() # when the user has already won the game   
    ERROR = auto()

    # multi step games
    NOT_FINISHED = auto() # when the user has not finished the dice game

FAST_RESPONSES = [RESULT_CODES.LAST_ATTEMPT, RESULT_CODES.ALREADY_PLAYED, RESULT_CODES.ALREADY_PLAYED_GAMES, RESULT_CODES.ALREADY_WON, RESULT_CODES.NOT_FINISHED]

slot_machine_values = {
    1: {"result": ("bar", "bar", "bar"), "win": True},
    2: {"result": ("grape", "bar", "bar"), "win": False},
    3: {"result": ("lemon", "bar", "bar"), "win": False},
    4: {"result": ("seven", "bar", "bar"), "win": False},
    5: {"result": ("bar", "grape", "bar"), "win": False},
    6: {"result": ("grape", "grape", "bar"), "win": False},
    7: {"result": ("lemon", "grape", "bar"), "win": False},
    8: {"result": ("seven", "grape", "bar"), "win": False},
    9: {"result": ("bar", "lemon", "bar"), "win": False},
    10: {"result": ("grape", "lemon", "bar"), "win": False},
    11: {"result": ("lemon", "lemon", "bar"), "win": False},
    12: {"result": ("seven", "lemon", "bar"), "win": False},
    13: {"result": ("bar", "seven", "bar"), "win": False},
    14: {"result": ("grape", "seven", "bar"), "win": False},
    15: {"result": ("lemon", "seven", "bar"), "win": False},
    16: {"result": ("seven", "seven", "bar"), "win": False},
    17: {"result": ("bar", "bar", "grape"), "win": False},
    18: {"result": ("grape", "bar", "grape"), "win": False},
    19: {"result": ("lemon", "bar", "grape"), "win": False},
    20: {"result": ("seven", "bar", "grape"), "win": False},
    21: {"result": ("bar", "grape", "grape"), "win": False},
    22: {"result": ("grape", "grape", "grape"), "win": True},
    23: {"result": ("lemon", "grape", "grape"), "win": False},
    24: {"result": ("seven", "grape", "grape"), "win": False},
    25: {"result": ("bar", "lemon", "grape"), "win": False},
    26: {"result": ("grape", "lemon", "grape"), "win": False},
    27: {"result": ("lemon", "lemon", "grape"), "win": False},
    28: {"result": ("seven", "lemon", "grape"), "win": False},
    29: {"result": ("bar", "seven", "grape"), "win": False},
    30: {"result": ("grape", "seven", "grape"), "win": False},
    31: {"result": ("lemon", "seven", "grape"), "win": False},
    32: {"result": ("seven", "seven", "grape"), "win": False},
    33: {"result": ("bar", "bar", "lemon"), "win": False},
    34: {"result": ("grape", "bar", "lemon"), "win": False},
    35: {"result": ("lemon", "bar", "lemon"), "win": False},
    36: {"result": ("seven", "bar", "lemon"), "win": False},
    37: {"result": ("bar", "grape", "lemon"), "win": False},
    38: {"result": ("grape", "grape", "lemon"), "win": False},
    39: {"result": ("lemon", "grape", "lemon"), "win": False},
    40: {"result": ("seven", "grape", "lemon"), "win": False},
    41: {"result": ("bar", "lemon", "lemon"), "win": False},
    42: {"result": ("grape", "lemon", "lemon"), "win": False},
    43: {"result": ("lemon", "lemon", "lemon"), "win": True},
    44: {"result": ("seven", "lemon", "lemon"), "win": False},
    45: {"result": ("bar", "seven", "lemon"), "win": False},
    46: {"result": ("grape", "seven", "lemon"), "win": False},
    47: {"result": ("lemon", "seven", "lemon"), "win": False},
    48: {"result": ("seven", "seven", "lemon"), "win": False},
    49: {"result": ("bar", "bar", "seven"), "win": False},
    50: {"result": ("grape", "bar", "seven"), "win": False},
    51: {"result": ("lemon", "bar", "seven"), "win": False},
    52: {"result": ("seven", "bar", "seven"), "win": False},
    53: {"result": ("bar", "grape", "seven"), "win": False},
    54: {"result": ("grape", "grape", "seven"), "win": False},
    55: {"result": ("lemon", "grape", "seven"), "win": False},
    56: {"result": ("seven", "grape", "seven"), "win": False},
    57: {"result": ("bar", "lemon", "seven"), "win": False},
    58: {"result": ("grape", "lemon", "seven"), "win": False},
    59: {"result": ("lemon", "lemon", "seven"), "win": False},
    60: {"result": ("seven", "lemon", "seven"), "win": False},
    61: {"result": ("bar", "seven", "seven"), "win": False},
    62: {"result": ("grape", "seven", "seven"), "win": False},
    63: {"result": ("lemon", "seven", "seven"), "win": False},
    64: {"result": ("seven", "seven", "seven"), "win": True},
}

def checkMonthlyWins(user: str) -> int:
    try:
        with open(DICE_FILE_PATH, 'r') as file:
            data = yaml.safe_load(file)
    except FileNotFoundError:
        data = {}
    if data is None:
        data = {}

    today = date.today()
    user_data: UserAttempts = data.get(user, {})
    montly_attempts = user_data.get(today.year, {})
    if not montly_attempts: return 0

    wins = 0
    for month in montly_attempts:
        month_data = montly_attempts[month]
        for day in month_data:
            day_data = month_data[day]
            if day_data.get("win", False):
                wins += 1
    return wins

def checkAllMonthlyWins() -> Dict[str, int]:
    try:
        with open(DICE_FILE_PATH, 'r') as file:
            data = yaml.safe_load(file)
    except FileNotFoundError:
        data = {}
    if data is None:
        data = {}

    monthly_wins = {}
    for user, user_data in data.items():
        wins = checkMonthlyWins(user)
        monthly_wins[user] = wins
    return monthly_wins

def getTodayAttempts(user: str) -> Dict[str, List[int]]:
    try:
        with open(DICE_FILE_PATH, 'r') as file:
            data = yaml.safe_load(file)
    except FileNotFoundError:
        data = {}
    if data is None:
        data = {}

    today = date.today()
    user_data: UserAttempts = data.get(user, {})
    year_attempts = user_data.get(today.year, {})
    month_attempts = year_attempts.get(today.month, {})
    user_attempts = month_attempts.get(today.day, {})
    win = user_attempts.get("win", False)
    if user_attempts:
        user_attempts.pop("win", None)
    return user_attempts, win

def setTodayAttempts(user: str, attempts: Dict[str, List[int]], win: bool) -> None:
    try:
        with open(DICE_FILE_PATH, 'r') as file:
            data = yaml.safe_load(file)
    except FileNotFoundError:
        data = {}
    if data is None:
        data = {}

    attempts["win"] = win

    today = date.today()
    user_data: UserAttempts = data.get(user, {})
    year_attempts = user_data.get(today.year, {})
    month_attempts = year_attempts.get(today.month, {})
    month_attempts[today.day] = attempts
    year_attempts[today.month] = month_attempts
    user_data[today.year] = year_attempts
    data[user] = user_data

    with open(DICE_FILE_PATH, 'w') as file:
        yaml.dump(data, file)

def update_game_attempt(
    user: str, 
    value: int, 
    game_type: str,
    win_condition_checker: Callable[[List[int]], Tuple[bool, RESULT_CODES]],
    daily_attempts: int = 2,
    log_prefix: str = "🎮"
) -> Tuple[bool, RESULT_CODES]:
    """
    General function to handle game attempts for different game types.
    
    Args:
        user: The userid
        value: The game value/result
        game_type: Type of game ("slot" or "dice")
        win_condition_checker: Function to check if the current state constitutes a win
        log_prefix: Prefix for log messages
        
    Returns:
        Tuple of (won, result_code)
    """
    log.info(f"{log_prefix} - User: {user}, Value: {value}")
    
    try:
        # Get current attempts
        user_attempts, win = getTodayAttempts(user)
        log.info(f"User attempts: {user_attempts}, win: {win}")
        game_attempts = user_attempts.get(game_type, [])
        
        # Check conditions
        if win:
            return False, RESULT_CODES.ALREADY_WON
        
        if len(game_attempts) >= daily_attempts:
            return False, RESULT_CODES.ALREADY_PLAYED
            
        if (MAX_MONTHLY_WINS) and (checkMonthlyWins(user) >= MAX_MONTHLY_WINS):
            return False, RESULT_CODES.ALREADY_WON
            
        # Add new attempt
        game_attempts.append(value)
        user_attempts[game_type] = game_attempts
        
        if (MAX_GAMES_PER_DAY) and (len(user_attempts) > MAX_GAMES_PER_DAY):
            return False, RESULT_CODES.ALREADY_PLAYED_GAMES
        
        # Check win conditions based on the specific game rules
        won, code = win_condition_checker(game_attempts, daily_attempts)
        
        # Save updated attempts
        setTodayAttempts(user, user_attempts, won)
        return won, code
        
    except Exception as e:
        log.error(e)
        return False, RESULT_CODES.ERROR

def check_slot_win(attempts: List[int], daily_attempts) -> Tuple[bool, RESULT_CODES]:
    """Check if slot machine attempts result in a win."""
    latest_value = attempts[-1]
    won = slot_machine_values[latest_value]["win"]
    
    if won:
        return True, RESULT_CODES.WON
    elif len(attempts) < daily_attempts:
        return False, RESULT_CODES.LAST_ATTEMPT
    else:
        return False, RESULT_CODES.LOST

def check_dice_win(attempts: List[int], daily_attempts) -> Tuple[bool, RESULT_CODES]:
    """Check if dice game attempts result in a win."""
    if len(attempts) < daily_attempts:
        return False, RESULT_CODES.NOT_FINISHED
    
    # Win condition: both dice show the same value
    won = attempts[0] == attempts[1]
    code = RESULT_CODES.WON if won else RESULT_CODES.LOST
    
    return won, code

def check_bulls_eye_win(attempts: List[int], daily_attempts) -> Tuple[bool, RESULT_CODES]:
    """Check if bulls eye game attempts result in a win."""
    if (len(attempts) < daily_attempts):
        if attempts[0] == 6:
            return False, RESULT_CODES.NOT_FINISHED
        else:
            return False, RESULT_CODES.LOST
    else:
        if attempts[0] != 6:
            return False, RESULT_CODES.ALREADY_PLAYED
    
    # Win condition: both dice show the same value
    won = attempts[0] == 6 and attempts[1] == 6
    code = RESULT_CODES.WON if won else RESULT_CODES.LOST
    
    return won, code

def check_and_update_slot(user: str, value: int) -> Tuple[bool, RESULT_CODES]:
    """Check and update slot machine game for a user."""
    return update_game_attempt(
        user=user,
        value=value,
        game_type="slot",
        win_condition_checker=check_slot_win,
        daily_attempts=2,
        log_prefix=Dice.SLOT_MACHINE
    )

def check_and_update_dice(user: str, value: int) -> Tuple[bool, RESULT_CODES]:
    """Check and update dice game for a user."""
    return update_game_attempt(
        user=user,
        value=value,
        game_type="dice",
        win_condition_checker=check_dice_win,
        daily_attempts=2,
        log_prefix=Dice.DICE
    )

def check_and_update_bulls_eye(user: str, value: int) -> Tuple[bool, RESULT_CODES]:
    """Check and update bulls eye game for a user."""
    return update_game_attempt(
        user=user,
        value=value,
        game_type="bulls_eye",
        win_condition_checker=check_bulls_eye_win,
        daily_attempts=2,
        log_prefix=Dice.DARTS
    )