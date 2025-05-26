import textwrap
from enum import Enum
from typing import Callable, Optional, Tuple, TypeVar, Union

from telegram import Update, Message
from telegram.ext import ContextTypes
from utils.escape import escape_protected_chars
from utils.auth.auth import Chat, chat_restricted
from utils.messages.todo.todo_db import (
    TodoItem,
    add_todo_item,
    get_todo_item_by_message_id,
    set_todo_item_message_id,
    set_todo_item_network,
    set_todo_item_priority,
    set_todo_item_status,
)
import logging
import os

mode = os.getenv('MODE')

log = logging.getLogger("todo")
chat = Chat(-1002364188805, 66325)  # Active todos chat
completed_chat = Chat(-1002364188805, 72686)  # Completed todos chat

debug_chat = Chat(-1002351154885, 8)
debug_completed_chat = Chat(-1002351154885, 2)  
if mode != "prod" and mode != "PROD":
    chat = debug_chat
    completed_chat = debug_completed_chat

T = TypeVar('T', bound=Union[TodoItem.Status, TodoItem.Priority])

class UpdateType(Enum):
    STATUS = "status"
    PRIORITY = "priority"
    NETWORK = "network"


async def _common_update_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    update_type: UpdateType,
    update_func: Callable,
    value_type: Optional[type] = None,
    move_on_status_change: bool = False
) -> None:
    """
    Common handler for todo item updates.
    
    Args:
        update: The update object
        context: The context object
        update_type: The type of update (status, priority, network)
        update_func: The function to call to update the todo item
        value_type: The enum type to convert the value to (if applicable)
        move_on_status_change: Whether to move the item between chats when status changes
    """
    # Get original todo item
    original_todo_message_id = update.message.reply_to_message.id
    original_todo_item = get_todo_item_by_message_id(original_todo_message_id)
    
    if original_todo_item is None:
        await update.effective_message.reply_text(
            text="Non riesco a trovare il todo a cui stai rispondendo",
            do_quote=False,
        )
        return
    
    # Extract and convert the value
    raw_value = update.message.text.lower()[len(update_type.value) + 1:].strip()
    
    if value_type:
        try:
            value = value_type[raw_value.upper()]
        except (KeyError, ValueError):
            await update.effective_message.reply_text(
                text=f"Valore non valido per {update_type.value}",
                do_quote=False,
            )
            return
    else:
        value = raw_value
    
    # Update the todo item
    updated_todo = update_func(original_todo_item.id, value)
    
    # Handle status updates that require moving the todo between chats
    if move_on_status_change and update_type == UpdateType.STATUS:
        current_chat = update.effective_chat
        
        if value == TodoItem.Status.DONE:
            # Move from active to completed chat
            target_chat = completed_chat
            source_chat = current_chat
        elif original_todo_item.status == TodoItem.Status.DONE:
            # Move from completed back to active chat
            target_chat = chat
            # target_chat = debug_chat
            source_chat = current_chat
        else:
            # No need to move, just update in place
            await context.bot.edit_message_text(
                chat_id=current_chat.id,
                message_id=original_todo_message_id,
                text=escape_protected_chars(f"{updated_todo}"),
                parse_mode="MarkdownV2",
            )
            await _try_delete_message(update.message)
            return
        
        # Send to target chat and update message ID in DB
        new_message = await context.bot.send_message(
            chat_id=target_chat.id,
            message_thread_id=target_chat.thread_id,
            text=escape_protected_chars(f"{updated_todo}"),
            parse_mode="MarkdownV2",
        )
        
        # Update the message ID in the database
        set_todo_item_message_id(updated_todo.id, new_message.message_id)
        
        # Delete the original message
        try:
            await context.bot.delete_message(
                chat_id=source_chat.id,
                message_id=original_todo_message_id,
            )
        except Exception as e:
            log.error(f"Error deleting message: {e}")
    else:
        # Update the original message
        await context.bot.edit_message_text(
            chat_id=update.effective_chat.id,
            message_id=original_todo_message_id,
            text=escape_protected_chars(f"{updated_todo}"),
            parse_mode="MarkdownV2",
        )
    
    # Delete the command message
    await _try_delete_message(update.message)


async def _try_delete_message(message) -> None:
    """Attempt to delete a message, log but ignore errors."""
    try:
        await message.delete()
    except Exception as e:
        log.error(f"Error deleting message: {e}")


async def status_update_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await _common_update_handler(
        update=update,
        context=context,
        update_type=UpdateType.STATUS,
        update_func=set_todo_item_status,
        value_type=TodoItem.Status,
        move_on_status_change=True
    )


async def priority_update_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await _common_update_handler(
        update=update,
        context=context,
        update_type=UpdateType.PRIORITY,
        update_func=set_todo_item_priority,
        value_type=TodoItem.Priority
    )


async def network_update_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await _common_update_handler(
        update=update,
        context=context,
        update_type=UpdateType.NETWORK,
        update_func=set_todo_item_network
    )


def _message_to_handler(text: str) -> Optional[Callable]:
    """
    Convert a message text to a handler function.
    """
    text_lower = text.lower()

    # Map of command prefixes to (handler_function, value_type, valid_values)
    handler_map = {
        UpdateType.STATUS.value: (
            status_update_handler, 
            TodoItem.Status,
            [status.value.lower() for status in TodoItem.Status]
        ),
        UpdateType.PRIORITY.value: (
            priority_update_handler,
            TodoItem.Priority,
            [priority.value.lower() for priority in TodoItem.Priority]
        ),
        UpdateType.NETWORK.value: (
            network_update_handler,
            None,
            None
        )
    }
    
    for prefix, (handler, enum_type, valid_values) in handler_map.items():
        if text_lower.startswith(f"{prefix} "):
            value = text_lower[len(prefix) + 1:].strip()
            
            # For network, any non-empty value is valid
            if prefix == UpdateType.NETWORK.value:
                if value:
                    return handler
            # For other types, check against valid values
            elif valid_values and value in valid_values:
                return handler
    
    return None


@chat_restricted([chat, completed_chat], notify=False)
async def todoInfo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Send a message with the available answers to messages handled by _message_to_handler.
    """
    statuses = [status.value for status in TodoItem.Status]
    priorities = [priority.value for priority in TodoItem.Priority]
    message = textwrap.dedent(
        f"""
        Per modificare lo stato o la priorità di un todo, rispondi al messaggio del todo con uno dei seguenti comandi:
        
        *Risposte disponibili:*
        
        *Status:*
        {', '.join(statuses)}
        
        *Priority:*
        {', '.join(priorities)}

        *Network:*
        _nome del network_ (es. `TUKO`, `HOLLE`)
        
        *Esempi di risposte:*
        status {statuses[0]}
        priority {priorities[0]}
        network holle
        """
    )

    # Send the message
    await update.effective_message.reply_text(
        message,
        do_quote=False,
        parse_mode="MarkdownV2",
    )


@chat_restricted([chat], notify=False)
async def addTodo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    todo_text = update.message.text
    todo_item = TodoItem(
        text=todo_text,
        user_id=update.effective_user.id,
    )

    # Add the todo item to the database
    todo_item = add_todo_item(todo_item)

    # Send a new message with the todo item
    message = await update.effective_message.reply_text(
        text=escape_protected_chars(f"{todo_item}"),
        parse_mode="MarkdownV2",
        do_quote=False,
    )
    set_todo_item_message_id(todo_item.id, message.message_id)
    
    # Delete the original message
    await _try_delete_message(update.message)


@chat_restricted([chat, completed_chat], notify=False)
async def updateTodo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle updates to todo items from both active and completed chats.
    """
    update_text = update.message.text
    log.debug(f"Update text: {update_text}")
    log.debug(f"Replied message: {update.message.reply_to_message.text}")
    
    handler = _message_to_handler(update_text)
    if handler:
        await handler(update, context)
    else:
        await update.effective_message.reply_text(
            text="errore nella richiesta di update, manda /todoinfo per vedere i comandi disponibili",
            do_quote=False,
        )


@chat_restricted([chat, completed_chat], notify=False)
async def deleteUnwantedMessage(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Delete the message that triggered the command.
    """
    await _try_delete_message(update.message)