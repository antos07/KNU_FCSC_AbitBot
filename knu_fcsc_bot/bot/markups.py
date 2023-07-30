from dataclasses import dataclass, asdict
from typing import Any

from telegram import User, InlineKeyboardMarkup, InlineKeyboardButton
from telegram._utils.types import ReplyMarkup

from knu_fcsc_bot.models import AbitChatInfo


@dataclass
class TextMarkup:
    """A generic text message markup that can be converted
    into keyword arguments for ptb bot methods"""

    text: str = None
    reply_markup: ReplyMarkup = None
    disable_web_page_preview: bool = None

    def to_kwargs(self) -> dict[str, Any]:
        """Converts this markup into keyword arguments for ptb bot methods"""
        return {
            name: value
            for name, value in asdict(self).items()
            if value is not None
        }


def get_new_user_greeting_markup(abit_chat_info: AbitChatInfo,
                                 user: User) -> TextMarkup:
    """Builds a greeting text message for a new chat user with all the info"""
    markup = TextMarkup()
    markup.text = f'👋 {user.mention_html()}, вітаю в чаті абітурієнтів ФКНК!'
    markup.reply_markup = InlineKeyboardMarkup.from_column([
        InlineKeyboardButton(
            text='🎓 Освітні програми',
            callback_data='programs',
        ),
        InlineKeyboardButton(
            text='📎 Корисні посилання',
            callback_data='useful_links',
        ),
        InlineKeyboardButton(
            text='🗑 Флудилка',
            url=abit_chat_info.flood_chat_link,
        ),
    ])
    return markup
