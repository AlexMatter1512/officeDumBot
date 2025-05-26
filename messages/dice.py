from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from utils.messages.dice.dice_util_v2 import (
    get_monthly_players,
    play_bowling,
    play_bulls_eye,
    play_dice,
    play_slot_machine,
    play_basket,
    play_soccer,
)
from utils.auth.auth import chat_restricted, Chat

from var.messages.dice.slot import getMessage, FAST_RESPONSES, RESULT_CODES, getWinAnimFile, Game
import asyncio
import logging

log = logging.getLogger("dice")
chats = [Chat(-1002364188805, 25544), Chat(-4594212673), Chat(-1002351154885)]

async def _handle_game(update: Update, check_function, wonAnimation=None):
    """Common handler for dice games."""
    composed_user = f"{update.effective_user.username}_!_{update.effective_user.id}"
    won, code = check_function(composed_user, update.message.dice.value)
    if code not in FAST_RESPONSES:
        await asyncio.sleep(3)  # Delay to avoid spoilers
    if won and code != RESULT_CODES.ALREADY_PLAYED:
        if wonAnimation:
            with open(wonAnimation, "rb") as file:
                await update.effective_message.reply_photo(
                    photo=file,
                    caption=f"Vincita di {update.effective_user.first_name}!\n{getMessage(code)}",
                )
        else:
            await update.effective_message.reply_text(
                text=f"Vincita di {update.effective_user.first_name}!\n{getMessage(code)}",
            )
    else:
        await update.effective_message.reply_text(text=getMessage(code), do_quote=True)


@chat_restricted(chats)
async def dice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the dice roll."""
    await _handle_game(update, play_dice, getWinAnimFile(Game.DICE))


@chat_restricted(chats)
async def slot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the slot machine roll."""
    await _handle_game(update, play_slot_machine, getWinAnimFile(Game.SLOT_MACHINE))


@chat_restricted(chats)
async def bullseye(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the bullseye roll."""
    await _handle_game(update, play_bulls_eye, getWinAnimFile(Game.DARTS))


@chat_restricted(chats)
async def bowling(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the bowling roll."""
    await _handle_game(update, play_bowling, getWinAnimFile(Game.BOWLING))


@chat_restricted(chats)
async def basket(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the basketball roll."""
    await _handle_game(update, play_basket, getWinAnimFile(Game.BASKETBALL))


@chat_restricted(chats)
async def soccer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the soccer roll."""
    await _handle_game(update, play_soccer)


@chat_restricted(chats)
async def spattemu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """divide the input by the number of players"""
    # if not (update.message.text.split()[0] == "
    try:
        cost = int(update.message.text.split()[1])
    except (IndexError, ValueError):
        await update.effective_message.reply_text(
            text="Usage: spattemu <cost of pranz>"
        )
        return
    players = get_monthly_players()
    log.debug(f"Players: {players}")
    if len(players) < 0:
        await update.effective_message.reply_text(text="No players found")
        return
    each = cost / len(players)
    message = f"V'ata spattiri: `{cost}`€,\n"
    message += f"Siti `{len(players)}` christiani,\n"
    message += f"Avissa veniri `{each}`€ a testa mbare\\.\n"

    await update.effective_message.reply_text(
        text=message,
        parse_mode=ParseMode.MARKDOWN_V2,
    )
