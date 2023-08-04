import html
from dataclasses import dataclass, asdict
from typing import Any, NamedTuple

from telegram import (User, InlineKeyboardMarkup, InlineKeyboardButton,
                      PhotoSize, )
from telegram._utils.types import ReplyMarkup, FileInput

from knu_fcsc_bot.models import AbitChatInfo, Program, UsefulLink


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
class PhotoMarkup(BaseMarkup):
    """A generic photo message markup that can be converted
    into keyword arguments for ptb bot methods"""
    photo: FileInput | PhotoSize = None
    caption: str = None
    reply_markup: ReplyMarkup = None

    def to_kwargs(self, *, caption_only: bool = False) -> dict[str, Any]:
        kwargs = super().to_kwargs()
        if caption_only and 'photo' in kwargs:
            del kwargs['photo']
        return kwargs


@dataclass
class AlertMarkup(BaseMarkup):
    text: str = None
    show_alert: bool = None


def _build_main_page_of_info_menu_reply_markup(
        abit_chat_info: AbitChatInfo
) -> ReplyMarkup:
    return InlineKeyboardMarkup.from_column([
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


def get_new_user_greeting_markup(abit_chat_info: AbitChatInfo,
                                 user: User) -> PhotoMarkup:
    """Builds a greeting text message for a new chat user with all the info"""
    markup = PhotoMarkup()
    markup.photo = abit_chat_info.greeting_photo_file_id
    markup.caption = (f'👋 {user.mention_html()}, вітаю в чаті '
                      f'абітурієнтів ФКНК!')
    markup.reply_markup = _build_main_page_of_info_menu_reply_markup(
        abit_chat_info=abit_chat_info
    )
    return markup


def get_program_list_markup(programs: list[Program],
                            requested_by: User) -> PhotoMarkup:
    """Builds a text message with program list as inline buttons"""
    markup = PhotoMarkup()
    markup.caption = (f'<b>[📖Інформаційна довідка</b> для '
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


def get_program_detail_markup(program: Program,
                              requested_by: User) -> PhotoMarkup:
    """Builds program detail markup"""
    markup = PhotoMarkup()
    guide_url = html.escape(program.guide_url)
    markup.caption = (f'<b>[📖Інформаційна довідка</b> для '
                      f'{requested_by.mention_html()}<b>]</b>\n\n'
                      f'<b>💻 Освітня програма:</b> {program.title}\n\n'
                      f'<a href="{guide_url}">⚙️ Гайд по спеціальності ⚙️</a>')
    markup.reply_markup = InlineKeyboardMarkup.from_button(
        button=InlineKeyboardButton(
            text='🔙 Назад',
            callback_data='programs',
        )
    )
    return markup


def get_main_page_of_info_menu_markup(abit_chat_info: AbitChatInfo,
                                      requested_by: User) -> PhotoMarkup:
    """Builds main menu page without greetings"""
    markup = PhotoMarkup()
    markup.photo = abit_chat_info.greeting_photo_file_id
    markup.caption = (f'<b>[📖Інформаційна довідка</b> для '
                      f'{requested_by.mention_html()}<b>]</b>')
    markup.reply_markup = _build_main_page_of_info_menu_reply_markup(
        abit_chat_info=abit_chat_info
    )
    return markup


def get_useful_link_list_markup(useful_links: list[UsefulLink],
                                requested_by: User) -> PhotoMarkup:
    """Builds a text message with useful links as inline buttons"""
    markup = PhotoMarkup()
    markup.caption = (f'<b>[📖Інформаційна довідка</b> для '
                      f'{requested_by.mention_html()}<b>]</b>\n\n'
                      f'📎 Корисні посилання:')
    buttons = [
        InlineKeyboardButton(
            text=link.title,
            url=link.url,
        )
        for link in useful_links
    ]
    buttons += [
        InlineKeyboardButton(
            text='🔙 Назад',
            callback_data='main_menu'
        ),
    ]
    markup.reply_markup = InlineKeyboardMarkup.from_column(buttons)
    return markup


def get_message_has_no_file_id_markup() -> TextMarkup:
    return TextMarkup(
        text='Повідомлення не містить файлів',
    )


def get_display_file_id_markup(file_id: str,
                               file_unique_id: str) -> TextMarkup:
    return TextMarkup(
        text=f'file_id=<code>{html.escape(file_id)}</code>\n'
             f'file_unique_id=<code>{html.escape(file_unique_id)}</code>',
    )


def get_filters_reloaded_markup() -> TextMarkup:
    """A text message that notifies about successful filter reloading"""
    return TextMarkup(
        text='✅ Done'
    )


class UserPenguinCount(NamedTuple):
    user: User
    penguin_count: int


def get_top10_users_by_sent_penguins_markup(
        top10: list[UserPenguinCount],
) -> TextMarkup:
    """A text message with a list of the top 10 users by their sent
    penguins count. `top10` is assumed to be in descending order."""
    markup = TextMarkup()

    top3_emoji = '🥇🥈🥉'
    top3_lines = [
        f'{medal_emoji} {user.full_name} — {penguin_count}'
        for medal_emoji, (user, penguin_count) in zip(top3_emoji, top10[:3])
    ]
    rest_lines = [
        f'{i}. {user.full_name} — {penguin_count}'
        for i, (user, penguin_count) in enumerate(top10[3:], start=4)
    ]
    top10_lines = top3_lines + rest_lines
    markup.text = ('🏆🐧 Топ 10 відправників пінгвінчиків:\n\n'
                   + '\n'.join(top10_lines))
    return markup
