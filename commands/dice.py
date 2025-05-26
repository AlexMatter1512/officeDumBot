import logging
import datetime
from telegram.helpers import escape_markdown
from telegram.constants import ParseMode
from telegram import Update, ReplyKeyboardMarkup 
from telegram.ext import ContextTypes
from utils.auth.auth import chat_restricted, Chat
from var.messages.dice.showGames import message as games_keyboard_message
from utils.auth.auth import chat_restricted

from utils.messages.dice.dice_util_v2 import (
    get_monthly_players,
    check_all_monthly_wins
)

log = logging.getLogger(__name__)

chats = [Chat(-1002364188805, 25544), Chat(-4594212673), Chat(-1002351154885)]

@chat_restricted(chats)
async def show_games_keyboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show the games keyboard."""
    log.info("Showing games keyboard")
    reply_markup = ReplyKeyboardMarkup(
        keyboard=[
            ["🎲", "🎰", "🎯", "🏀", "🎳"]
        ],
        resize_keyboard=True,
        one_time_keyboard=False,
        input_field_placeholder="Choose a game",
    )
    await update.effective_message.reply_text(
        text=games_keyboard_message,
        parse_mode=ParseMode.MARKDOWN_V2,
        reply_markup=reply_markup,
    )

@chat_restricted(chats)
async def get_all_monthly_wins(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get the monthly wins."""
    # mm/yy format
    now = datetime.datetime.now()
    # message = "*Vincite mensili:*\n\n"
    message = f"*Vincite {now.month}/{now.year}*:\n"
    message += f"_aggiornate al {now.day}/{now.month}/{now.year}_\n\n"

    max = 0
    max_user = None
    for user, wins in sorted(
        check_all_monthly_wins().items(), key=lambda x: x[1], reverse=True
    ):
        log.debug(f"User: {user}, Wins: {wins}")
        # username = user.split("_!_")[0]
        # userid = user.split("_!_")[1]
        username, userid = user.split("_!_")
        identifier = username if username != "None" else userid

        message += escape_markdown(f"{wins}: {identifier}\n")

        if wins > max:
            max = wins
            max_user = identifier

    if max_user:
        # check for ties
        tied_users = [
            identifier
            for identifier, wins in check_all_monthly_wins().items()
            if wins == max
        ]
        if len(tied_users) > 1:
            message += f"\nCi sono {len(tied_users)} utenti con {max} vincite:\n"
            for tied_user in tied_users:
                tied_username, tied_userid = tied_user.split("_!_")
                tied_identifier = (
                    tied_username if tied_username != "None" else tied_userid
                )
                message += escape_markdown(f"{tied_identifier}\n")
        else:
            message += f"\nIl più vincente è *{escape_markdown(max_user)}* con {max} vincite\\!\n"

    monthly_players = get_monthly_players()

    monthly_players_string = f"\n**>GIOCATORI MENSILI:\n>\n"
    for user in monthly_players:
        username, userid = user.split("_!_")
        identifier = username if username != "None" else userid
        monthly_players_string += ">\\- " + escape_markdown(f"{identifier}\n")

    monthly_players_string = monthly_players_string.rstrip("\n") + "||"
    message += monthly_players_string

    log.debug(f"Message: {message}")
    await update.effective_message.reply_text(
        text=message, parse_mode=ParseMode.MARKDOWN_V2
    )


