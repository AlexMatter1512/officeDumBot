import logging
import re
from telegram import Message, Update
from telegram.helpers import escape_markdown
from telegram.ext import ContextTypes
import utils.messages.dumb.mbarometro_util_v2 as mbarometro_util
from utils.messages.dumb.utils import find_word
from var.messages.dumb import MediaInfo, PREPUZIO, LETSGOSKY, CARTOCCIATA, RECORDED, CEO
from var.messages import SendMediaErrors

# Configure the "dumb" logger
log = logging.getLogger("dumb")


async def send_media_message(
    update: Update,
    media_info: MediaInfo,
    quote_text: str = None,
):
    media_methods = {
        "photo": update.message.reply_photo,
        "audio": update.message.reply_audio,
        "animation": update.message.reply_animation,
    }
    # text_message: str = media_info.TEXT_MESSAGE
    # media_param_name: str = media_info.MEDIA_TYPE
    # tg_file_id: str = media_info.TG_FILE_ID
    # file_location: str = media_info.FILE_LOCATION
    text_message: str = media_info.text_message
    media_param_name: str = media_info.media_type
    tg_file_id: str = media_info.tg_file_id
    file_location: str = media_info.file_location
    error_message: str = SendMediaErrors.DEFAULT

    await update.effective_message.reply_text(
        text_message,
        quote=(
            update.message.build_reply_arguments(quote=quote_text)
            if quote_text
            else False
        ),
    )
    # try to send the media file using the file_id
    send_media_method = media_methods.get(media_param_name)
    if not send_media_method:
        log.error(f"Invalid media_param_name: {media_param_name}")
        return
    try:
        await send_media_method(
            **{media_param_name: tg_file_id},
            # do_quote= update.message.build_reply_arguments(quote=quote_text) if quote_text else False,
            # do_quote=update.message.build_reply_arguments(quote="Quoted Text")
        )
    except Exception as e:
        log.error(e)
        # if the file_id is not valid, try to send the media file using the file_location
        if file_location:
            try:
                with open(file_location, "rb") as media_file:
                    image: Message = await send_media_method(
                        **{media_param_name: media_file}, do_quote=False
                    )
                    # await update.effective_chat.send_message(text="sent from file", reply_to_message_id=image.message_id)
            except Exception as e:
                log.error(e)
                await update.effective_message.reply_text(e, do_quote=False)
        elif file_location != 0:
            await update.effective_message.reply_text(error_message, do_quote=False)


async def letsgosky(update: Update, context: ContextTypes.DEFAULT_TYPE, match=None):
    await send_media_message(
        update=update,
        media_info=LETSGOSKY,
        quote_text=match
    )


async def prepuzio(update: Update, context: ContextTypes.DEFAULT_TYPE, match=None):
    await send_media_message(
        update=update,
        media_info=PREPUZIO,
        quote_text=match
    )


async def cartocciata(update: Update, context: ContextTypes.DEFAULT_TYPE, match=None):
    await send_media_message(
        update=update,
        media_info=CARTOCCIATA,
        quote_text=match
    )


async def recorded(update: Update, context: ContextTypes.DEFAULT_TYPE, match=None):
    await send_media_message(
        update=update,
        media_info=RECORDED,
        quote_text=match
    )


async def ceo(update: Update, context: ContextTypes.DEFAULT_TYPE, match=None):
    await send_media_message(
        # update=update, media_info=CEO, quote_text=find_word("ceo", update.message.text)
        update=update,
        media_info=CEO,
        quote_text=match
    )


async def eee(update: Update, context: ContextTypes.DEFAULT_TYPE, match=None):
    name = (
        update.effective_user.first_name
        if update.effective_user.first_name
        else "mbare"
    )
    await update.effective_message.reply_text("EEEEEE " + name.upper(), do_quote=(update.message.build_reply_arguments(quote=match) if match else False))


async def mbarometro(update: Update, context: ContextTypes.DEFAULT_TYPE, match=None):
    # log.info (update.message)
    user = update.effective_user.username or (
        update.effective_user.first_name or ""
    ) + (" " + (update.effective_user.last_name or str(update.effective_user.id)))
    actual_message_text = update.message.text or update.message.caption or ""
    # mbare_message_count = update.message.text.lower().count("mbare")
    mbare_message_count = len(re.findall(r"\bmbare\b", actual_message_text, re.IGNORECASE))
    user_count, total = mbarometro_util.increment(user, mbare_message_count)

    text = "*Mbarometro* 📊\n\n"
    text += f"This message contains: {mbare_message_count}\n"
    text += f"{escape_markdown(user)} total count: {user_count}"
    if user_count % 10 == 0:
        text += " 🎉\n\n"
    else:
        text += "\n\n"
    for user in mbarometro_util.get_all():
        text += f"{escape_markdown(user['user'])} : {user['value']}\n"
    text += f"\nTotal count: {total}"
    if total % 100 == 0:
        text += " 🎉"

    # do_quote = False
    # mbare_word = find_word("mbare", actual_message_text)
    # if mbare_word:
    #     do_quote = update.message.build_reply_arguments(quote=mbare_word)
    # # await update.effective_message.reply_text(text, do_quote=update.message.build_reply_arguments(quote=find_word("mbare", update.message.text)), parse_mode="MarkdownV2")
    # await update.effective_message.reply_text(
    #     text, do_quote=do_quote, parse_mode="MarkdownV2"
    # )
    await update.effective_message.reply_text(
        text,
        do_quote=(update.message.build_reply_arguments(quote=match) if match else False),
        parse_mode="MarkdownV2",
    )


async def no_audio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.effective_message.reply_text(
        f"EEEEEE {update.effective_user.first_name.upper()} NON MANDARE AUDIO CHE NON LI VUOLE ASCOLTARE NESSUNO"
    )


# map message with its handler
handler_mapping = {
    re.compile(r"ceo", re.IGNORECASE): ceo,
    re.compile(r"^[eE]{2,}", re.IGNORECASE): eee,
    re.compile(r"mbare", re.IGNORECASE): mbarometro,
    re.compile(r"prepuzio|monella", re.IGNORECASE): prepuzio,
    re.compile(r"letsgosky|letsgoski", re.IGNORECASE): letsgosky,
    re.compile(
        r"cartocciata|cartocciate|panino|pranzo|pizzetta|ettore", re.IGNORECASE
    ): cartocciata,
    re.compile(
        r"cazzo|minchia|buttana|troia|droga|pisello|pistola", re.IGNORECASE
    ): recorded,
}

async def handle_dumb_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle dumb messages based on the regex patterns defined in handler_mapping.
    """
    log.debug(f"Received message: {update.message.text}")
    log.debug(f"Received caption: {update.message.caption}")

    to_check = update.message.text or update.message.caption
    for pattern, handler in handler_mapping.items():
        match = re.search(pattern, to_check)
        # if re.search(pattern, to_check):
        if match:
            # If a match is found, call the corresponding handler
            log.debug(f"Matched pattern: {pattern.pattern}")
            # log.debug(f"Match: {re.search(pattern, to_check).group(0)}")
            log.debug(f"Match: {match.group(0)}")
            log.debug(f"Calling handler: {handler.__name__}")
            await handler(update, context, match.group(0))
            # break , # to stop after the first match