from telegram import Update
from telegram.ext import ContextTypes
import utils.commands.list_util_v2 as list_util

# Function to add a new lavagnetta item
async def addLavagnetta(update: Update, context: ContextTypes.DEFAULT_TYPE):
    item_item = ' '.join(context.args)
    if not item_item:
        await update.message.reply_text("Please specify a lavagnetta item.")
        return

    list_util.add_item(item_item, "lav")  # Use the utility function

    await update.message.reply_text(f"Added item: {item_item}")

# Function to list all items with indexes
async def lavagnetta(update: Update, context: ContextTypes.DEFAULT_TYPE):
    items = list_util.get_all_items("lav")  # Use the utility function

    if not items:
        await update.message.reply_text("No items.")
        return

    # Add an index to each lavagnetta item
    items_text = "\n".join([f"{index + 1}. {item.strip()}" for index, item in enumerate(items)])
    await update.message.reply_text(f"items:\n{items_text}")

# Function to remove a lavagnetta item by index
async def removeLavagnetta(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        index = int(context.args[0]) - 1  # Get the index from the command arguments
    except (IndexError, ValueError):
        await update.message.reply_text("Please provide a valid item index to remove.")
        return

    removed_item = list_util.remove_item_by_index(index, "lav")  # Use the utility function

    if removed_item:
        await update.message.reply_text(f"Removed item: {removed_item}")
    else:
        await update.message.reply_text("Invalid item index.")