from utils.auth.users_db import insert_new_user, UserDbCodes
from telegram import Update
from telegram.ext import ContextTypes

async def addme(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Add a user to the database."""
    if update.effective_user:
        user_id = update.effective_user.id
        username = update.effective_user.username
        first_name = update.effective_user.first_name
        last_name = update.effective_user.last_name
        language_code = update.effective_user.language_code
        is_admin = False

        # Add the user to the database
        code = insert_new_user(user_id, username, first_name, last_name, language_code, is_admin)
        if code == UserDbCodes.USER_ALREADY_EXISTS.value:
            await update.effective_message.reply_text(
                text="Sei già un utente autorizzato!",
            )
            return
        elif code == UserDbCodes.SUCCESS.value:
            await update.effective_message.reply_text(
                text="Congratulazioni! Adesso puoi usare il bot.",
            )
            return
        else:
            await update.effective_message.reply_text(
                text="Si è verificato un errore durante la registrazione.",
            )
            return