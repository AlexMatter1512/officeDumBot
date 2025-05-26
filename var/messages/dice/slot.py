from enum import Enum, auto
import dotenv
from datetime import date
from telegram import Dice
from enum import StrEnum
from pathlib import Path

current_directory = Path(__file__).parent.absolute()

MAX_MONTHLY_WINS = None
MAX_GAMES_PER_DAY = 2

class Game(StrEnum):
    DICE = Dice.DICE
    DARTS = Dice.DARTS
    SLOT_MACHINE = Dice.SLOT_MACHINE
    FOOTBALL = Dice.FOOTBALL
    BASKETBALL = Dice.BASKETBALL
    BOWLING = Dice.BOWLING
# Disable for now
    # BASKETBALL = Dice.BASKETBALL
    # FOOTBALL = Dice.FOOTBALL
    # BOWLING = Dice.BOWLING

class RESULT_CODES(Enum):
    """Error codes for the dice game."""
    # for all games
    LOST = auto() # when the user has lost the game 
    WON = auto() # when the user has won the game 
    LAST_ATTEMPT = auto() # when the user has one attempt left 
    ALREADY_PLAYED = auto() # when the user has already played daily_attempts times
    LOST_PREVIOUSLY = auto() # when the user has lost the game previously and that game needs all wins
    ALREADY_PLAYED_GAMES = auto() # when the user has already played MAX_GAMES_PER_DAY games
    ALREADY_WON = auto() # when the user has already won the game   
    ERROR = auto()

    # multi step games
    NOT_FINISHED = auto() # when the user has not finished the dice game

FAST_RESPONSES = [RESULT_CODES.LAST_ATTEMPT, RESULT_CODES.ALREADY_PLAYED, RESULT_CODES.ALREADY_PLAYED_GAMES, RESULT_CODES.ALREADY_WON, RESULT_CODES.NOT_FINISHED]

def getWinAnimFile(game: Game) -> str:
    path = current_directory / "res" 
    if game == Game.BASKETBALL:
        path = path / "basket_win.jpg"
    elif game == Game.SLOT_MACHINE:
        path = path / "slot_win.jpg"
    elif game == Game.DICE:
        path = path / "dice_win.jpg"
    elif game == Game.DARTS:
        path = path / "darts_win.jpg"
    elif game == Game.FOOTBALL:
        path = path / "football_win.jpg"
    elif game == Game.BOWLING:
        path = path / "bowling_win.jpg"
    return str(path)

def getMessage(code: RESULT_CODES) -> str:
    """Return the message for the given code."""
    messages = {
        RESULT_CODES.LOST: "Hai perso! huuuuuuuugh",
        RESULT_CODES.WON: "Bravo mbare!",
        RESULT_CODES.LAST_ATTEMPT: "Peccato mbare!",
        RESULT_CODES.ALREADY_PLAYED: "Hai già giocato a questo gioco per oggi!",
        RESULT_CODES.LOST_PREVIOUSLY: "Hai già perso in precedenza, questo gioco richiede solo vittorie!",
        RESULT_CODES.ALREADY_PLAYED_GAMES: f"Hai già giocato a {MAX_GAMES_PER_DAY} giochi oggi!",
        RESULT_CODES.ALREADY_WON: "Hai già vinto mbare, non mi puoi fare spendere tutto il monthly tuning!",
        RESULT_CODES.NOT_FINISHED: "Incrocia le dita🤞🏼!",
        RESULT_CODES.ERROR: "Errore!",
    }
    return messages[code]

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
