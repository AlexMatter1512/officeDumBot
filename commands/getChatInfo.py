from telegram import Update
from telegram.ext import ContextTypes
from utils.auth.auth import protected_handler
import textwrap

@protected_handler(notify=False)
async def getChatInfo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # await context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")
    chat = update.effective_chat
    message = update.effective_message

    chat_info = textwrap.dedent(f"""
        *Chat ID:*
        `{chat.id}`
        
        *Thread ID:*
        `{message.message_thread_id}`
        
        *Chat Title:*
        `{chat.title}`
        
        *Chat Type:*
        `{chat.type}`
        
        *Chat Username:*
        `{chat.username}`
        
        *Chat First Name:*
        `{chat.first_name}`
        
        *Chat Last Name:*
        `{chat.last_name}`
        
        *Message User ID:*
        `{message.from_user.id}`
        
        *Message User First Name:*
        `{message.from_user.first_name}`
        
        *Message User Last Name:*
        `{message.from_user.last_name}`
        
        *Message User Username:*
        `{message.from_user.username}`
        
        """).strip()
    await update.effective_message.reply_text(chat_info, do_quote=False, parse_mode="MarkdownV2")