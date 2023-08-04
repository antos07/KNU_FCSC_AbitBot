from telegram import Update
from telegram.ext import (Application, ChatMemberHandler, CallbackQueryHandler,
                          CommandHandler, filters, MessageHandler,
                          TypeHandler, )

from knu_fcsc_bot.bot import callbacks


def setup_handlers(app: Application) -> None:
    """Setup handlers for the given application"""
    app.add_error_handler(callback=callbacks.unhandled_exception)

    # Record chat members before any other handler, but using
    # a lower group to allow this update to be handled by other
    # handlers.
    app.add_handler(TypeHandler(
        type=Update,
        callback=callbacks.chat_member_recorder,
    ), group=-1)

    # Skip messages from all chats, except allowed chats
    allowed_chat_filter = filters.Chat()
    app.bot_data['allowed_chat_filter'] = allowed_chat_filter
    app.add_handler(MessageHandler(
        filters=~allowed_chat_filter,
        callback=callbacks.message_from_not_allowed_chat,
    ))

    # Logging when this bot is added to chats
    app.add_handler(ChatMemberHandler(
        callback=callbacks.my_chat_member_updated,
        chat_member_types=ChatMemberHandler.MY_CHAT_MEMBER,
    ))

    # Greetings for new chat members
    app.add_handler(ChatMemberHandler(
        callback=callbacks.chat_member_updated,
        chat_member_types=ChatMemberHandler.CHAT_MEMBER,
        block=False,
    ))

    # Info menu actions
    app.add_handlers([
        CallbackQueryHandler(
            callback=callbacks.cd_programs,
            pattern=r'^programs$',
            block=False,
        ),
        CallbackQueryHandler(
            callback=callbacks.cd_program_by_id,
            pattern=r'^program_by_id:(?P<id>\d+)$',
            block=False,
        ),
        CallbackQueryHandler(
            callback=callbacks.cd_main_menu,
            pattern=r'^main_menu$',
            block=False,
        ),
        CallbackQueryHandler(
            callback=callbacks.cd_useful_links,
            pattern=r'^useful_links$',
            block=False,
        ),
    ])

    # Commands
    app.add_handlers([
        CommandHandler(
            command='info',
            callback=callbacks.cmd_info,
            filters=filters.ChatType.GROUPS,
            block=False,
        ),
        CommandHandler(
            command='file_id',
            callback=callbacks.cmd_file_id,
            block=False,
        ),
        CommandHandler(
            command='reload_filters',
            callback=callbacks.cmd_reload_filters,
            block=False,
        ),
        CommandHandler(
            command='top_penguins',
            callback=callbacks.cmd_top_penguins,
            block=False,
        ),
    ])

    # Pinguin counter
    app.add_handler(MessageHandler(
        filters=filters.ANIMATION,
        callback=callbacks.animation_message,
    ))
