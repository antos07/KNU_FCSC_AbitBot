import datetime
import html
from dataclasses import dataclass, asdict
from typing import Any, NamedTuple, Protocol

from dateutil.tz import gettz
from telegram import (User, InlineKeyboardMarkup, InlineKeyboardButton,
                      PhotoSize, )
from telegram._utils.types import ReplyMarkup, FileInput

from knu_fcsc_bot.models import (AbitChatInfo, Program, UsefulLink,
                                 AdmissionCommitteInfo, )

KYIV_TZ = gettz('Europe/Kyiv')


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
    button_column = [
        InlineKeyboardButton(
            text='🎓 Освітні програми',
            callback_data='programs',
        ),
    ]
    if abit_chat_info.admission_committe_info:
        button_column += [
            InlineKeyboardButton(
                text='🏫 Приймальна комісія',
                callback_data='admission_committe',
            ),
        ]
    button_column += [
        InlineKeyboardButton(
            text='📎 Корисні посилання',
            callback_data='useful_links',
        ),
        InlineKeyboardButton(
            text='🗑 Флудилка',
            url=abit_chat_info.flood_chat_link,
        ),
    ]
    return InlineKeyboardMarkup.from_column(button_column)


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


class TimetableRecord(Protocol):
    """A generic timetable record protocol"""

    date: datetime.date
    work_start: datetime.time
    work_end: datetime.time


def _choose_timetable_record_emoji(record: TimetableRecord) -> str:
    """Returns an emoji base on the date.

    ✅ for passed days
    🔴 for the actual date
    ☑ for next dates
    """
    passed_record = '✅'
    actual_record = '🔴'
    future_record = '☑'

    now = datetime.datetime.now(tz=KYIV_TZ)
    if record.date < now.date():
        return passed_record
    if record.date == now.date():
        if now.time() < record.work_start:
            return future_record
        if record.work_end < now.time():
            return passed_record
        return actual_record
    return future_record


def _build_timetable_text(
        timetable: list[TimetableRecord],
) -> str:
    """Builds a timetable text"""
    timetable_record_format = ('{emoji} {record.date:%d.%m} '
                               '{record.work_start:%H:%M}-'
                               '{record.work_end:%H:%M}')
    timetable_lines = [
        timetable_record_format.format(
            record=record,
            emoji=_choose_timetable_record_emoji(record),
        )
        for record in timetable
    ]
    return '\n'.join(timetable_lines)


def get_admission_committe_info_markup(
        admission_committe_info: AdmissionCommitteInfo,
        requested_by: User,
) -> PhotoMarkup:
    """A photo message with the committe timetable in its caption
    and online queue, required documents and "how to find?" links as
    inline buttons"""
    markup = PhotoMarkup()
    markup.photo = admission_committe_info.chat.greeting_photo_file_id
    markup.caption = (f'<b>[📖Інформаційна довідка</b> для '
                      f'{requested_by.mention_html()}<b>]</b>\n\n'
                      f'🏫 Приймальна комісія\n\n'
                      f'Розклад:\n')
    markup.caption += _build_timetable_text(
        timetable=admission_committe_info.timetable)
    buttons = []
    if admission_committe_info.queue_url:
        buttons.append(InlineKeyboardButton(
            text='🕒 ЕЛЕКТРОННА ЧЕРГА',
            url=admission_committe_info.queue_url,
        ))
    if admission_committe_info.required_documents_url:
        buttons.append(InlineKeyboardButton(
            text='📂 НЕОБХІДНІ ДОКУМЕНТИ',
            url=admission_committe_info.required_documents_url,
        ))
    buttons += [
        InlineKeyboardButton(
            text='🗺️📌 Як нас знайти?',
            url='https://goo.gl/maps/yH3CN9Quy7DEruvg7',
        ),
        InlineKeyboardButton(
            text='🔙 Назад',
            callback_data='main_menu'
        ),
    ]
    markup.reply_markup = InlineKeyboardMarkup.from_column(
        button_column=buttons,
    )
    return markup
