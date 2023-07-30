import html
from dataclasses import dataclass, asdict
from typing import Any

from telegram import User, InlineKeyboardMarkup, InlineKeyboardButton
from telegram._utils.types import ReplyMarkup

from knu_fcsc_bot.models import AbitChatInfo, Program


@dataclass
class BaseMarkup:
    def to_kwargs(self) -> dict[str, Any]:
        """Converts this markup into keyword arguments for ptb bot methods"""
        return {
            name: value
            for name, value in asdict(self).items()
            if value is not None
        }


@dataclass
class TextMarkup(BaseMarkup):
    """A generic text message markup that can be converted
    into keyword arguments for ptb bot methods"""

    text: str = None
    reply_markup: ReplyMarkup = None
    disable_web_page_preview: bool = None


@dataclass
class AlertMarkup(BaseMarkup):
    text: str = None
    show_alert: bool = None


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


def get_program_list_markup(programs: list[Program],
                            requested_by: User) -> TextMarkup:
    """Builds a text message with program list as inline buttons"""
    markup = TextMarkup()
    markup.text = (f'<b>[📖Інформаційна довідка</b> для '
                   f'{requested_by.mention_html()}<b>]</b>\n\n'
                   f'🎓Освітні програми:')
    program_buttons = [
        InlineKeyboardButton(
            text=program.title,
            callback_data=f'program_by_id:{program.id}'
        )
        for program in
        programs
    ]
    markup.reply_markup = InlineKeyboardMarkup.from_column(program_buttons + [
        InlineKeyboardButton(
            text='🔙 Назад',
            callback_data='main_menu'
        ),
    ])
    return markup


def get_program_not_found_alert_markup() -> AlertMarkup:
    """Builds an alert message for not found program"""
    return AlertMarkup(
        text='Програми не існує. Зверніться до адмінів чату',
        show_alert=True
    )


def get_program_detail_markup(program: Program, requested_by) -> TextMarkup:
    """Builds program detail markup"""
    markup = TextMarkup()
    guide_url = html.escape(program.guide_url)
    markup.text = (f'<b>[📖Інформаційна довідка</b> для '
                   f'{requested_by.mention_html()}<b>]</b>\n\n'
                   f'<b>💻 Освітня програма:</b> Прикладна математика (113)\n\n'
                   f'<a href="{guide_url}">⚙️ Гайд по спеціальності ⚙️</a>')
    markup.reply_markup = InlineKeyboardMarkup.from_button(
        button=InlineKeyboardButton(
            text='🔙 Назад',
            callback_data='programs',
        )
    )
    markup.disable_web_page_preview = True
    return markup
