from contextlib import suppress
from datetime import timedelta

from loguru import logger
from telegram import Update
from telegram.error import TelegramError
from telegram.ext import CallbackContext

from knu_fcsc_bot import usecases
from knu_fcsc_bot.bot import markups
from knu_fcsc_bot.bot.utils import (did_new_user_join,
                                    schedule_message_deletion,
                                    reschedule_message_deletion_on_interaction,
                                    get_file_id, is_a_penguin_gif,
                                    get_cached_chat_member, )

DELETE_INFO_MENU_AFTER = timedelta(minutes=5)
DELETE_DEV_MESSAGES_AFTER = timedelta(minutes=1)
DELETE_MISC_MESSAGE_AFTER = timedelta(minutes=3)


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

    session = context.bot_data['AsyncSession']()
    async with session:
        try:
            info = await usecases.get_main_abit_chat_info_usecase(session,
                                                                  chat.id)
        except usecases.DoesNotExist:
            # Ignoring unsupported chat
            return

    markup = markups.get_new_user_greeting_markup(info, user)
    message = await chat.send_photo(**markup.to_kwargs())

    schedule_message_deletion(
        job_queue=context.job_queue,
        message=message,
        after=DELETE_INFO_MENU_AFTER,
    )


@reschedule_message_deletion_on_interaction(DELETE_INFO_MENU_AFTER)
async def cd_programs(update: Update,
                      context: CallbackContext) -> None:
    """Lists all available programs for this chat"""
    user = update.effective_user
    chat = update.effective_chat
    logger.info(f'{user} requested program list in {chat}')

    session = context.bot_data['AsyncSession']()
    async with session:
        programs = await usecases.list_programs_usecase(session, chat.id)

    markup = markups.get_program_list_markup(programs, user)
    await update.effective_message.edit_caption(**markup.to_kwargs(
        caption_only=True,
    ))


@reschedule_message_deletion_on_interaction(DELETE_INFO_MENU_AFTER)
async def cd_program_by_id(update: Update,
                           context: CallbackContext) -> None:
    """Displays info about program by its id"""
    program_id = int(context.match.group('id'))
    user = update.effective_user
    chat = update.effective_chat
    logger.info(f'{user} requested program with id={program_id} in {chat}')

    session = context.bot_data['AsyncSession']()
    async with session:
        try:
            program = await usecases.get_program_by_id_usecase(session,
                                                               program_id)
        except usecases.DoesNotExist:
            markup = markups.get_program_not_found_alert_markup()
            await update.callback_query.answer(**markup.to_kwargs(),
                                               cache_time=60)
            return

    markup = markups.get_program_detail_markup(program, user)
    await update.effective_message.edit_caption(**markup.to_kwargs(
        caption_only=True,
    ))


@reschedule_message_deletion_on_interaction(DELETE_INFO_MENU_AFTER)
async def cd_main_menu(update: Update, context: CallbackContext) -> None:
    """Displays main page of info menu"""
    user = update.effective_user
    chat = update.effective_chat
    logger.info(f'{user} requested main page of info menu in {chat}')

    session = context.bot_data['AsyncSession']()
    async with session:
        abit_chat_info = await usecases.get_main_abit_chat_info_usecase(
            session=session,
            chat_id=chat.id,
        )

    markup = markups.get_main_page_of_info_menu_markup(abit_chat_info, user)
    await update.effective_message.edit_caption(**markup.to_kwargs(
        caption_only=True,
    ))


@reschedule_message_deletion_on_interaction(DELETE_INFO_MENU_AFTER)
async def cd_useful_links(update: Update, context: CallbackContext) -> None:
    """Displays a list of useful links as an inline keyboard"""
    user = update.effective_user
    chat = update.effective_chat
    logger.info(f'{user} requested useful links in {chat}')

    session = context.bot_data['AsyncSession']()
    async with session:
        useful_links = await usecases.list_useful_links_usecase(session,
                                                                chat.id)

    markup = markups.get_useful_link_list_markup(useful_links, user)
    await update.effective_message.edit_caption(**markup.to_kwargs(
        caption_only=True,
    ))


@reschedule_message_deletion_on_interaction(DELETE_INFO_MENU_AFTER)
async def cd_admission_committe(update: Update,
                                context: CallbackContext) -> None:
    """Displays the info about the admission committe"""
    user = update.effective_user
    chat = update.effective_chat
    logger.info(f'{user} requested the info about the admission '
                f'committe {chat}')

    session = context.bot_data['AsyncSession']()
    async with session:
        admission_committe_info = (
            await usecases.get_admission_committe_info_usecase(
                session=session,
                chat_id=chat.id,
            )
        )

    markup = markups.get_admission_committe_info_markup(
        admission_committe_info=admission_committe_info,
        requested_by=user,
    )
    await update.effective_message.edit_caption(
        **markup.to_kwargs(caption_only=True)
    )


async def cmd_info(update: Update, context: CallbackContext) -> None:
    """Displays main page of info menu"""
    user = update.effective_user
    chat = update.effective_chat
    logger.info(f'{user} requested main page of info menu via /info in {chat}')

    session = context.bot_data['AsyncSession']()
    async with session:
        try:
            abit_chat_info = await usecases.get_main_abit_chat_info_usecase(
                session=session,
                chat_id=chat.id,
            )
        except usecases.DoesNotExist:
            # Ignoring unsupported chat
            return

    markup = markups.get_main_page_of_info_menu_markup(abit_chat_info, user)
    message = await update.effective_message.reply_photo(**markup.to_kwargs())

    schedule_message_deletion(
        job_queue=context.job_queue,
        message=message,
        after=DELETE_INFO_MENU_AFTER,
        with_reply_to=True,
    )


async def cmd_file_id(update: Update, context: CallbackContext) -> None:
    """A utility command for displaying the file_id of an attachment"""
    user = update.effective_user
    chat = update.effective_chat
    message = update.effective_message
    logger.info(f'{user} requested file_id of {message} in {chat}')

    file_id_tuple = get_file_id(message.reply_to_message)
    if file_id_tuple:
        markup = markups.get_display_file_id_markup(*file_id_tuple)
    else:
        markup = markups.get_message_has_no_file_id_markup()
    await message.reply_text(**markup.to_kwargs())


async def message_from_not_allowed_chat(update: Update,
                                        context: CallbackContext) -> None:
    """Logs update from not allowed chat"""
    message = update.effective_message
    chat = update.effective_chat
    logger.info(f'{chat} is not allowed: {message}')


async def my_chat_member_updated(update: Update,
                                 context: CallbackContext) -> None:
    """Logs when bot is added to a new chat"""
    if not did_new_user_join(update.my_chat_member):
        return
    logger.info(f'Bot is added to {update.effective_chat}')


async def cmd_reload_filters(update: Update, context: CallbackContext) -> None:
    """Reloads allowed chat filter by adding missing chats from the db"""
    logger.debug('Reloading filters')

    session = context.bot_data['AsyncSession']()
    async with session:
        allowed_chat_ids = await usecases.list_allowed_chat_ids_usecase(
            session=session,
        )

    # Adding allowed chat ids to the filter. Chat filter uses a set
    # internally, so there is no need to check whether these chats
    # were added before.
    allowed_chat_filter = context.bot_data['allowed_chat_filter']
    allowed_chat_filter.add_chat_ids(allowed_chat_ids)

    logger.info(f'Updated allowed chats: {list(allowed_chat_filter.chat_ids)}')

    markup = markups.get_filters_reloaded_markup()
    replied_message = await update.effective_message.reply_text(
        **markup.to_kwargs()
    )

    schedule_message_deletion(
        job_queue=context.job_queue,
        message=replied_message,
        after=DELETE_DEV_MESSAGES_AFTER,
        with_reply_to=True,
    )


async def animation_message(update: Update,
                            context: CallbackContext) -> None:
    """Records penguin gifs in abit chats"""
    animation = update.effective_message.animation
    if not is_a_penguin_gif(animation):
        return

    user = update.effective_user
    chat = update.effective_chat
    logger.info(f'{user} sent the penguin gif in {chat}')

    session = context.bot_data['AsyncSession']()
    async with session:
        await usecases.record_penguin_gif_usecase(session=session,
                                                  user_id=user.id,
                                                  chat_id=chat.id,
                                                  timestamp=update.effective_message.date)
        await session.commit()

    logger.debug(f'Recorded a penguin from {user} in {chat}')


async def chat_member_recorder(update: Update,
                               context: CallbackContext) -> None:
    """Saves the user as chat member of the corresponding chat"""
    chat = update.effective_chat
    user = update.effective_user
    if not chat or not user:
        # Can not determine the member of the chat
        return

    session = context.bot_data['AsyncSession']()
    async with session:
        with suppress(usecases.DoesNotExist):
            await usecases.record_chat_member(session, user.id, chat.id)
        await session.commit()

    logger.debug(f'Recorded {user} as a member of {chat}')


async def cmd_top_penguins(update: Update, context: CallbackContext) -> None:
    """Displays the Top 10 users with the most sent penguin gifs"""
    user = update.effective_user
    chat = update.effective_chat
    logger.info(f'{user} requested top 10 penguins in {chat}')

    session = context.bot_data['AsyncSession']()
    async with session:
        top10 = await usecases.top_users_with_most_sent_penguins_usecase(
            session=session, chat_id=chat.id)
    # Getting an actual chat member for each user_id
    top10 = (
        (await get_cached_chat_member(chat, user_id), penguin_count)
        for user_id, penguin_count in top10
    )
    # Building a list of markups.UserPenguinCount
    top10 = [
        markups.UserPenguinCount(chat_member.user, penguin_count)
        async for chat_member, penguin_count in top10
    ]

    markup = markups.get_top10_users_by_sent_penguins_markup(top10)
    sent_message = await update.effective_message.reply_text(
        **markup.to_kwargs()
    )

    schedule_message_deletion(
        job_queue=context.job_queue,
        message=sent_message,
        after=DELETE_MISC_MESSAGE_AFTER,
        with_reply_to=True,
    )


async def message_via_forbidden_bot(update: Update,
                                    context: CallbackContext) -> None:
    """Trys to delete a message sent via a forbidden bot"""
    message = update.effective_message
    logger.info(f'{message.from_user} sent a message via '
                f'forbidden {message.via_bot}')

    with suppress(TelegramError):
        await message.delete()
