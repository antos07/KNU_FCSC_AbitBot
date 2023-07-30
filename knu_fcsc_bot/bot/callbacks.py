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


async def cd_program_by_id(update: Update,
                           context: CallbackContext) -> None:
    """Displays info about program by its id"""
    program_id = int(context.match.group('id'))
    user = update.effective_user
    chat = update.effective_chat
    logger.info(f'{user} requested program with id={program_id} in {chat}')

    try:
        program = await usecases.get_program_by_id_usecase(program_id)
    except usecases.DoesNotExist:
        markup = markups.get_program_not_found_alert_markup()
        await update.callback_query.answer(**markup.to_kwargs(), cache_time=60)
        return

    markup = markups.get_program_detail_markup(program, user)
    await update.effective_message.edit_text(**markup.to_kwargs())
