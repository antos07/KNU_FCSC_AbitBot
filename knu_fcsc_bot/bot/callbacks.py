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
        # Using of f-string resulted in a wierd exception. So
        # here update kwarg is passed to the logger.
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


async def cd_main_menu(update: Update, context: CallbackContext) -> None:
    """Displays main page of info menu"""
    user = update.effective_user
    chat = update.effective_chat
    logger.info(f'{user} requested main page of info menu in {chat}')

    abit_chat_info = await usecases.get_main_abit_chat_info_usecase(chat.id)

    markup = markups.get_main_page_of_info_menu_markup(abit_chat_info, user)
    await update.effective_message.edit_text(**markup.to_kwargs())


async def cd_useful_links(update: Update, context: CallbackContext) -> None:
    """Displays a list of useful links as an inline keyboard"""
    user = update.effective_user
    chat = update.effective_chat
    logger.info(f'{user} requested useful links in {chat}')

    useful_links = await usecases.list_useful_links_usecase(chat.id)

    markup = markups.get_useful_link_list_markup(useful_links, user)
    await update.effective_message.edit_text(**markup.to_kwargs())
