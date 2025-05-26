from telegram import Update
from telegram.ext import ContextTypes

from utils.auth.auth import chat_restricted, Chat

chat = Chat(-1002351154885, 2) 

@chat_restricted([chat])
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # await context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")
    await update.effective_message.reply_text(
        text="Sono attivo mbare",
        do_quote=False,
    )