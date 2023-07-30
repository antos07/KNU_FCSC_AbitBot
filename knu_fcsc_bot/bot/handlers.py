from telegram.ext import (Application, ChatMemberHandler, CallbackQueryHandler,
                          CommandHandler, filters, )

from knu_fcsc_bot.bot import callbacks


def setup_handlers(app: Application) -> None:
    """Setup handlers for the given application"""
    app.add_error_handler(callback=callbacks.unhandled_exception)

    # Greetings for new chat members
    app.add_handler(ChatMemberHandler(
        callback=callbacks.chat_member_updated,
        chat_member_types=ChatMemberHandler.CHAT_MEMBER,
    ))

    # Info menu actions
    app.add_handlers([
        CallbackQueryHandler(
            callback=callbacks.cd_programs,
            pattern=r'^programs$'
        ),
        CallbackQueryHandler(
            callback=callbacks.cd_program_by_id,
            pattern=r'^program_by_id:(?P<id>\d+)$',
        ),
        CallbackQueryHandler(
            callback=callbacks.cd_main_menu,
            pattern=r'^main_menu$',
        ),
        CallbackQueryHandler(
            callback=callbacks.cd_useful_links,
            pattern=r'^useful_links$',
        ),
    ])

    # Commands
    app.add_handlers([
        CommandHandler(
            command='info',
            callback=callbacks.cmd_info,
            filters=filters.ChatType.GROUPS,
        ),
    ])
