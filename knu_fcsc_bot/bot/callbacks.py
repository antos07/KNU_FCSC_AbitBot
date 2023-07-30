from loguru import logger
from telegram import Update
from telegram.ext import CallbackContext

from knu_fcsc_bot.bot.utils import did_new_user_join


async def chat_member_updated(update: Update,
                              context: CallbackContext) -> None:
    """Says hello to a new user in a chat"""
    if not did_new_user_join(update.chat_member):
        return

    user = update.effective_user
    chat = update.effective_chat
    logger.info(f'{user} joined {chat}')

    await chat.send_message(f'Hello, {user.mention_html()}!')
