from telegram.ext import Application, ChatMemberHandler

from knu_fcsc_bot.bot import callbacks


def setup_handlers(app: Application) -> None:
    """Setup handlers for the given application"""
    app.add_handler(ChatMemberHandler(
        callback=callbacks.chat_member_updated,
        chat_member_types=ChatMemberHandler.CHAT_MEMBER,
    ))
