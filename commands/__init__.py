# import handlers first so the enum can access them
from .start import start
from .getChatInfo import getChatInfo
from .lavagnetta import addLavagnetta, lavagnetta, removeLavagnetta
from .dice import show_games_keyboard, get_all_monthly_wins

# from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Optional

from telegram import BotCommand

@dataclass(frozen=True, slots=True)
class CommandDef:
    cmd: str
    desc: str
    handler: Optional[Callable] = None       # sync or async callable

    @property
    def bot_command(self) -> BotCommand:
        """Object that telegram.Bot.set_my_commands expects"""
        return BotCommand(self.cmd, self.desc)

class Commands(Enum):
    START          = CommandDef("start",        "health-check",                    start)
    TODOINFO       = CommandDef("todoinfo",     "instructions for updating todos", None)
    ADDLAVAGNETTA  = CommandDef("addlavagnetta","add a new lavagnetta item",       addLavagnetta)
    LISTLAVAGNETTA = CommandDef("lavagnetta",   "list all lavagnetta items",       lavagnetta)
    REMOVELAVAGNETTA = CommandDef("removelavagnetta", "remove a lavagnetta item",  removeLavagnetta)
    GETWINS        = CommandDef("getwins",      "get wins at gambling games",      get_all_monthly_wins)
    PLAY           = CommandDef("play",         "show games keyboard",             show_games_keyboard)
    GETCHATINFO    = CommandDef("getchatinfo",  "get chat info",                   getChatInfo)

    # ------------- convenience passthroughs -------------
    @property
    def cmd(self) -> str:            # e.g. Commands.START.cmd  ->  "start"
        return self.value.cmd

    @property
    def desc(self) -> str:
        return self.value.desc

    @property
    def handler(self) -> Optional[Callable]:
        return self.value.handler

    @property
    def bot_command(self) -> BotCommand:
        return self.value.bot_command
