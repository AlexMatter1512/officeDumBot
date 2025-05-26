import logging
from .dice_db import (
    get_all_monthly_players,
    get_monthly_wins, 
    get_all_monthly_wins, 
    get_daily_attempts_count, 
    add_daily_game_attempt, 
    get_daily_games_count, 
    get_daily_attempts
)
from var.messages.dice.slot import Game, RESULT_CODES, MAX_GAMES_PER_DAY, MAX_MONTHLY_WINS, slot_machine_values
from datetime import date
from typing import List, Tuple

log = logging.getLogger("dice")

def handle_attempt(
    user: str,
    value: int,
    game: Game,
    actual_handler: callable,
    max_daily_attempts: int,
    needed_attempts: int = 1, # This is the number of attempts needed to complete the game
):
    log.debug(f"Handling attempt for {user} in {game} with value {value}")
    if max_daily_attempts < needed_attempts:
        max_daily_attempts = needed_attempts

    attempts = get_daily_attempts(user, game)
    log.debug(f"User {user} attempts for game {game}: {attempts}")
    # Check if the user has already played the game more than the allowed times for that game
    if get_daily_attempts_count(user, game) >= max_daily_attempts:
        return False, RESULT_CODES.ALREADY_PLAYED
    
    # Check if the user has already played MAX_GAMES_PER_DAY games
    daily_games_count = get_daily_games_count(user)
    log.debug(f"User {user} total daily games count: {daily_games_count}")
    
    if daily_games_count >= MAX_GAMES_PER_DAY:
        log.debug(f"User {user} reached max games per day: {MAX_GAMES_PER_DAY}")
        
        if len(attempts) >= needed_attempts:
            log.debug(f"User {user} has completed needed attempts: {len(attempts)} >= {needed_attempts}")
            return False, RESULT_CODES.ALREADY_PLAYED_GAMES
        
        if len(attempts) == 0:
            log.debug(f"User {user} has no attempts for this game yet. Since theyre not completing a game, they can't play.")
            return False, RESULT_CODES.ALREADY_PLAYED_GAMES

    # Check if the user won
    attempts.append(value)
    won, code = actual_handler(attempts, max_daily_attempts)
    add_daily_game_attempt(user, game, str(value), won)

    return won, code

# Actual handlers
def check_slot_win(attempts: List[int], daily_attempts) -> Tuple[bool, RESULT_CODES]:
    """Check if slot machine attempts result in a win."""
    latest_value = attempts[-1] # -1 is the last element in the list
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
    win_val = 6
    log.debug(f"Checking bulls eye win with attempts: {attempts}, dayly attempts: {daily_attempts}")
    if (len(attempts) < daily_attempts):
        if attempts[-1] == win_val:
            return False, RESULT_CODES.NOT_FINISHED
        else:
            return False, RESULT_CODES.LOST
    else:
        if attempts[-1] != win_val:
            return False, RESULT_CODES.LOST_PREVIOUSLY
    
    # Win condition: all attempts are 6
    won = all(attempt == win_val for attempt in attempts)
    code = RESULT_CODES.WON if won else RESULT_CODES.LOST
    
    return won, code

def check_basketSoccer_win(attempts: List[int], daily_attempts) -> Tuple[bool, RESULT_CODES]:
    """Check if basket game attempts result in a win."""
    win_values = [4, 5]
    # log.debug(f"Checking bulls eye win with attempts: {attempts}, dayly attempts: {daily_attempts}")
    log.debug(f"Checking basket or soccer win with attempts: {attempts}, dayly attempts: {daily_attempts}")
    if (len(attempts) < daily_attempts):
        if attempts[-1] in win_values:
            return False, RESULT_CODES.NOT_FINISHED
        else:
            return False, RESULT_CODES.LOST
    else:
        if attempts[-1] not in win_values:
            return False, RESULT_CODES.LOST_PREVIOUSLY
    
    # Win condition: all attempts are 4 or 5
    won = all(attempt in win_values for attempt in attempts)
    code = RESULT_CODES.WON if won else RESULT_CODES.LOST
    
    return won, code

def check_basket_win_single(attempts: List[int], daily_attempts) -> Tuple[bool, RESULT_CODES]:
    """Check if slot machine attempts result in a win."""
    win_values = [4, 5]
    latest_value = attempts[-1] # -1 is the last element in the list
    won = latest_value in win_values    
    if won:
        return True, RESULT_CODES.WON
    elif len(attempts) < daily_attempts:
        return False, RESULT_CODES.LAST_ATTEMPT
    else:
        return False, RESULT_CODES.LOST

def check_bulls_eye_win_single(attempts: List[int], daily_attempts) -> Tuple[bool, RESULT_CODES]:
    """Check if bulls eye game attempts result in a win."""
    win_val = 6
    latest_value = attempts[-1] # -1 is the last element in the list
    won = latest_value == win_val    
    if won:
        return True, RESULT_CODES.WON
    elif len(attempts) < daily_attempts:
        return False, RESULT_CODES.LAST_ATTEMPT
    else:
        return False, RESULT_CODES.LOST

def check_bowling_win_single(attempts: List[int], daily_attempts) -> Tuple[bool, RESULT_CODES]:
    """Check if bulls eye game attempts result in a win."""
    win_val = 6
    latest_value = attempts[-1] # -1 is the last element in the list
    won = latest_value == win_val    
    if won:
        return True, RESULT_CODES.WON
    elif len(attempts) < daily_attempts:
        return False, RESULT_CODES.LAST_ATTEMPT
    else:
        return False, RESULT_CODES.LOST
 

# play
def play_slot_machine(user: str, value: int) -> Tuple[bool, RESULT_CODES]:
    return handle_attempt(user, value, Game.SLOT_MACHINE, check_slot_win, 2, 2)

def play_dice(user: str, value: int) -> Tuple[bool, RESULT_CODES]:
    return handle_attempt(user, value, Game.DICE, check_dice_win, 2, 2)

def play_bulls_eye(user: str, value: int) -> Tuple[bool, RESULT_CODES]:
    # return handle_attempt(user, value, Game.DARTS, check_bulls_eye_win, 2, 2)
    return handle_attempt(user, value, Game.DARTS, check_bulls_eye_win_single, 2, 2)

def play_bowling(user: str, value: int) -> Tuple[bool, RESULT_CODES]:
    # return handle_attempt(user, value, Game.BOWLING, check_bulls_eye_win, 2, 2)
    return handle_attempt(user, value, Game.BOWLING, check_bowling_win_single, 2, 2)

def play_basket(user: str, value: int) -> Tuple[bool, RESULT_CODES]:
    # return handle_attempt(user, value, Game.BASKETBALL, check_basketSoccer_win, 2, 2)
    return handle_attempt(user, value, Game.BASKETBALL, check_basket_win_single, 2, 2)

def play_soccer(user: str, value: int) -> Tuple[bool, RESULT_CODES]:
    return handle_attempt(user, value, Game.FOOTBALL, check_basketSoccer_win, 2, 2)

#check
def check_monthly_wins(user: str) -> int:
    return get_monthly_wins(user, date.today().month, date.today().year)

def check_all_monthly_wins() -> dict:
    return get_all_monthly_wins(date.today().month, date.today().year)

def get_monthly_players() -> List[str]:
    return get_all_monthly_players(date.today().month, date.today().year)
