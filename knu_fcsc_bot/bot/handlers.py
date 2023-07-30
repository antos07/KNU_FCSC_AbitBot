from telegram.ext import Application, ChatMemberHandler, CallbackQueryHandler

from knu_fcsc_bot.bot import callbacks


def setup_handlers(app: Application) -> None:
    """Setup handlers for the given application"""
    app.add_error_handler(callback=callbacks.unhandled_exception)

    app.add_handler(ChatMemberHandler(
        callback=callbacks.chat_member_updated,
        chat_member_types=ChatMemberHandler.CHAT_MEMBER,
    ))

    app.add_handlers([
        CallbackQueryHandler(
            callback=callbacks.cd_programs,
            pattern=r'^programs$'
        ),
        CallbackQueryHandler(
            callback=callbacks.cd_program_by_id,
            pattern=r'^program_by_id:(?P<id>\d+)$',
        ),
    ])
