# Standard library imports
import logging
import re
import os

# Third-party imports
from telegram import BotCommand
from telegram.ext import (
    CommandHandler,
    MessageHandler,
    filters,
    Application,
)

# Local imports
from messages.dice import slot, dice, bullseye, soccer, basket, bowling, spattemu
from messages.dumb import (
    handler_mapping,
    handle_dumb_message,
)
from messages.addme import addme
from messages.todo_v2 import addTodo, updateTodo, todoInfo, chat, deleteUnwantedMessage

# from var.commands.Commands import Commands
from utils.messages.todo.messageReplyFilter import filter_todo_reply
from commands import Commands

log = logging.getLogger(__name__)
REGISTRATION_COMMAND = os.getenv("REGISTRATION_COMMAND")


def setup_handlers(application: Application) -> None:
    """Add all handlers to the application."""
    command_handlers = []
    for command in Commands:
        if command.handler is not None:
            handler = CommandHandler(
                command.cmd,
                command.handler,
            )
            command_handlers.append(handler)

    # Message handlers
    spattemu_handler = MessageHandler(
        filters.Regex(re.compile(r"spattemu", re.IGNORECASE)), spattemu
    )

    add_todo_handler = MessageHandler(filters.FORWARDED, addTodo)
    updateTodo_handler = MessageHandler(filter_todo_reply, updateTodo)
    unwanted_handler = MessageHandler(filters.Chat(chat.id), deleteUnwantedMessage)

    slot_handler = MessageHandler(filters.Dice.SLOT_MACHINE, slot)
    dice_handler = MessageHandler(filters.Dice.DICE, dice)
    bullseye_handler = MessageHandler(filters.Dice.DARTS, bullseye)
    soccer_handler = MessageHandler(filters.Dice.FOOTBALL, soccer)
    basket_handler = MessageHandler(filters.Dice.BASKETBALL, basket)
    bowling_handler = MessageHandler(filters.Dice.BOWLING, bowling)

    # Add command handlers to the application
    for handler in command_handlers:
        application.add_handler(handler)

    # DUMB HANDLERS
    for pattern, _ in handler_mapping.items():
        # Add a message handler for each pattern in the handler_mapping
        application.add_handler(
            MessageHandler(filters.Regex(pattern), handle_dumb_message)
        )
        application.add_handler(
            MessageHandler(filters.CaptionRegex(pattern), handle_dumb_message)
        )

    application.add_handler(
        add_todo_handler, group=1
    )  # group=1 to make sure it is processed after others
    application.add_handler(
        updateTodo_handler, group=1
    )  # group=1 to make sure it is processed after others
    application.add_handler(
        unwanted_handler, group=1
    )  # group=1 to make sure it is processed after others
    application.add_handler(slot_handler)
    application.add_handler(dice_handler)
    application.add_handler(bullseye_handler)
    application.add_handler(soccer_handler)
    application.add_handler(basket_handler)
    application.add_handler(bowling_handler)
    application.add_handler(spattemu_handler)

    if REGISTRATION_COMMAND is None:
        log.warning("a REGISTRATION_COMMAND is not set, new users won't be accepted")
    else:
        addme_handler = MessageHandler(
            filters.Regex(re.compile(REGISTRATION_COMMAND)),
            addme,
            block=False,
        )
        application.add_handler(addme_handler)
