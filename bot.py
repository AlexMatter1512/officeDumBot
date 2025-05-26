from dotenv import load_dotenv
from telegram import BotCommand
from telegram.ext import ApplicationBuilder, Application
from handlers import setup_handlers  # Import the function to setup handlers
import logging
import os

from utils.logging.logSetup import logSetup
from commands import Commands  # Import the Commands enum
# from var.commands.Commands import Commands

logger = logging.getLogger(__name__)

async def post_init(application: Application) -> None:
    # Create a list of BotCommand objects
    # commands = [value for _, value in Commands.__dict__.items() if isinstance(value, BotCommand)]
    commands = [command.bot_command for command in Commands]
    # Now set the commands using the externalized list
    await application.bot.set_my_commands(commands)

if __name__ == '__main__':
    load_dotenv()
    logSetup(os.getenv('LOG_LEVEL', 'INFO'))
    mode = os.getenv('MODE')
    # log the mode
    logger.info(f"Mode: {mode}")
    token = os.getenv('TOKEN') if mode == 'PROD' else os.getenv('TOKEN_DEV')
    application = ApplicationBuilder().token(token).post_init(post_init).build()

    setup_handlers(application)  # Call the function to setup handlers
    
    application.run_polling()
    
