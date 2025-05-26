from typing import List
from telegram import Update
from . import users_db
import logging

log = logging.getLogger("auth")

class Chat:
    id: int
    thread_id: int | None
    ignore_thread_id: bool

    def __init__(self, id: int, thread_id: int | None = None, ignore_thread_id: bool = False):
        self.id = id
        self.thread_id = thread_id
        self.ignore_thread_id = ignore_thread_id

    def __eq__(self, other):
        if not isinstance(other, Chat):
            return NotImplemented
        if self.ignore_thread_id:
            return self.id == other.id
        return self.id == other.id and self.thread_id == other.thread_id

def protected_handler(notify=False):
    def decorator(func):
        async def wrapper(update: Update, context):
            if not users_db.is_allowed_user(str(update.effective_user.id)):
                log.error(f"User {update.effective_user.id} is not allowed to use this command.")
                if notify:
                    await context.bot.send_message(
                        chat_id=update.effective_chat.id,
                        text="You are not authorized.",
                        reply_to_message_id=update.effective_message.message_id
                    )
                return
            return await func(update, context)
        return wrapper
    return decorator

def admin_only(notify=True):
    """
    Decorator to restrict a handler to admin users only.
    """
    def decorator(func):
        async def wrapper(update: Update, context):
            # Check if the user is an admin
            if not users_db.is_admin(str(update.effective_user.id)):
                # If not, send a message and return
                if notify:
                    await context.bot.send_message(
                        chat_id=update.effective_chat.id,
                        text="You are not authorized.",
                        reply_to_message_id=update.effective_message.message_id
                    )
                return
            return await func(update, context)
        return wrapper
    return decorator

def chat_restricted(chats:List[Chat], notify=True):
    """
    Decorator to restrict a handler to specific chats.
    """
    def decorator(func):
        async def wrapper(update: Update, context):
            log.debug(f"function: {func.__name__}")
            # Check if the chat ID and message thread ID are in the allowed list
            incoming_chat = Chat(update.effective_chat.id, update.effective_message.message_thread_id)
            if incoming_chat not in chats:
                logmethod = log.info if notify else log.debug
                # If not, send a message and return
                if notify:
                    await context.bot.send_message(
                        chat_id=update.effective_chat.id,
                        text="This command is not allowed in this chat.",
                        reply_to_message_id=update.effective_message.message_id
                    )
                logmethod(f"Chat {incoming_chat.id} not in allowed chats, skipping handler {func.__name__}")
                logmethod(f"Allowed chats: {[f'{chat.id}, {chat.thread_id}' for chat in chats]}")
                return
            return await func(update, context)
        return wrapper
    return decorator
