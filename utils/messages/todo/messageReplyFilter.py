from telegram.ext.filters import MessageFilter
import logging

log = logging.getLogger("todo reply filter")

class FilterTodoReply(MessageFilter):
    def filter(self, message):
        if not message.reply_to_message:
            return False
        if not message.reply_to_message.text:
            return False
        
        # log.debug(f"Filtering replied message text: {message.reply_to_message.text}")
        return message.reply_to_message.text.split()[0].lower() == "todo:"

# Remember to initialize the class.
filter_todo_reply = FilterTodoReply()