from loguru import logger
from telegram import Update
from telegram.ext import CallbackContext

from knu_fcsc_bot import usecases
from knu_fcsc_bot.bot import markups
from knu_fcsc_bot.bot.utils import did_new_user_join


async def chat_member_updated(update: Update,
                              context: CallbackContext) -> None:
    """Says hello to a new user in a chat"""
    user = update.effective_user
    chat = update.effective_chat
    if not did_new_user_join(update.chat_member) or user.is_bot:
        return
    logger.info(f'{user} joined {chat}')

    info = await usecases.get_main_abit_chat_info_usecase(chat.id)

    markup = markups.get_new_user_greeting_markup(info, user)
    await chat.send_message(**markup.to_kwargs())
