from loguru import logger
from telegram import Update
from telegram.ext import CallbackContext

from knu_fcsc_bot import usecases
from knu_fcsc_bot.bot import markups
from knu_fcsc_bot.bot.utils import did_new_user_join


async def unhandled_exception(update: Update | object | None,
                              context: CallbackContext) -> None:
    """Logs unhandled exceptions"""
    message = 'Unhandled exception'
    if update:
        message += ' while processing {update}'
    logger.exception(message, update=update, exception=context.error)


async def chat_member_updated(update: Update,
                              context: CallbackContext) -> None:
    """Sends basic info to a new chat member"""
    user = update.effective_user
    chat = update.effective_chat
    if not did_new_user_join(update.chat_member) or user.is_bot:
        return
    logger.info(f'{user} joined {chat}')

    info = await usecases.get_main_abit_chat_info_usecase(chat.id)

    markup = markups.get_new_user_greeting_markup(info, user)
    await chat.send_message(**markup.to_kwargs())


async def cd_programs(update: Update,
                      context: CallbackContext) -> None:
    """Lists all available programs for this chat"""
    user = update.effective_user
    chat = update.effective_chat
    logger.info(f'{user} requested program list in {chat}')

    programs = await usecases.list_programs_usecase(chat.id)

    markup = markups.get_program_list_markup(programs, user)
    await update.effective_message.edit_text(**markup.to_kwargs())
