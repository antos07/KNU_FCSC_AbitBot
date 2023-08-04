from contextlib import suppress
from datetime import timedelta, datetime
from functools import wraps
from typing import Callable, Any, TypeAlias

from loguru import logger
from telegram import (ChatMemberUpdated, ChatMember, Message, Update,
                      Animation,
                      Chat, )
from telegram.ext import JobQueue, CallbackContext


def did_new_user_join(chat_member_update: ChatMemberUpdated) -> bool:
    """Checks if chat memeber status update means that new user has joined"""
    # Code taken from PTB's example:
    # https://github.com/python-telegram-bot/python-telegram-bot/blob/master/examples/chatmemberbot.py
    status_change = chat_member_update.difference().get("status")
    old_is_member, new_is_member = chat_member_update.difference().get(
        "is_member", (None, None))

    if status_change is None:
        return False

    old_status, new_status = status_change
    was_member = old_status in [
        ChatMember.MEMBER,
        ChatMember.OWNER,
        ChatMember.ADMINISTRATOR,
    ] or (old_status == ChatMember.RESTRICTED and old_is_member is True)
    is_member = new_status in [
        ChatMember.MEMBER,
        ChatMember.OWNER,
        ChatMember.ADMINISTRATOR,
    ] or (new_status == ChatMember.RESTRICTED and new_is_member is True)

    return not was_member and is_member


def schedule_message_deletion(
        job_queue: JobQueue,
        message: Message,
        after: timedelta,
        with_reply_to: bool = False,
) -> None:
    """Schedules message deletion at `datetime.now() + after`. If
    `with_reply_to` is True, this also will delete the message, to which
    this message was a reply."""

    async def delete_message(context: CallbackContext) -> None:
        await message.delete()
        logger.info(f'Deleted {message}')
        if context.job:
            await message.reply_to_message.delete()
            logger.info(f'Deleted {message.reply_to_message}')

    user_id = None
    with suppress(AttributeError):
        # Trying to get user_id form message, if it exists.
        user_id = message.from_user.id

    job = job_queue.run_once(
        callback=delete_message,
        when=after,
        name=f'delete_message:{message.message_id}',
        chat_id=message.chat_id,
        user_id=user_id,
        data={'with_reply_to': with_reply_to},
    )
    logger.debug(f'Scheduled {message} for deletion ({with_reply_to=}) at'
                 f' {job.next_t}')


_Callback: TypeAlias = Callable[[Update, CallbackContext], Any]
_CallbackDecorator: TypeAlias = Callable[[_Callback], _Callback]


def reschedule_message_deletion_on_interaction(
        delete_after: timedelta
) -> _CallbackDecorator:
    """A decorator for a callback query handler callback function. Reschedules
    the message from the update to be deleted after `delete_after`"""

    def decorator(wrapped: _Callback) -> _Callback:
        @wraps(wrapped)
        async def wrapper(update: Update, context: CallbackContext) -> Any:
            message = update.effective_message
            logger.debug(f'Rescheduling {message}')
            job_name = f'delete_message:{message.message_id}'
            job_queue = context.job_queue

            # Removing old jobs
            old_jobs = job_queue.get_jobs_by_name(job_name)
            for job in old_jobs:
                job.schedule_removal()

            # Scheduling new job
            with_reply_to = any(job.data['with_reply_to'] for job in old_jobs)
            schedule_message_deletion(job_queue, message, delete_after,
                                      with_reply_to=with_reply_to)

            return await wrapped(update, context)

        return wrapper

    return decorator


def get_file_id(message: Message) -> tuple[str, str] | None:
    """Gets file_id and file_unique_id from message attachment. Returns None
    if none is given"""
    attachment = message.effective_attachment

    with suppress(TypeError):
        # Assuming that dealing with an array of photo sizes
        max_size = sorted(attachment,
                          key=lambda ps: (ps.width * ps.height))[-1]
        return max_size.file_id, max_size.file_unique_id

    try:
        return attachment.file_id, attachment.file_unique_id
    except AttributeError:
        return None


def is_a_penguin_gif(animation: Animation) -> bool:
    """Checks whether animation is a penguin gif by its file_unique_id"""
    penguin_gif_file_unique_ids = {
        'AQADfwADr7SkUnI',  # the ID recognized by @KNU_FCSC_AbitBot
        'AgADfwADr7SkUg',  # the id recognized by my test bot
    }
    return animation.file_unique_id in penguin_gif_file_unique_ids


class _GetCachedChatMember:
    """A wrapper around bot.get_chat_members that caches chat members
        for an hour"""

    DEFAULT_TIME_TO_LEAVE = timedelta(hours=1)

    def __init__(self, time_to_live: timedelta = DEFAULT_TIME_TO_LEAVE):
        self.time_to_live = time_to_live
        self.cache: dict[tuple[int, int], tuple[datetime, ChatMember]] = {}

    async def __call__(self, chat: Chat, user_id: int) -> ChatMember:
        try:
            self._remove_from_cache_if_expired(chat.id, user_id)
            return self.cache[chat.id, user_id][1]
        except KeyError:  # Not in cache
            chat_member = await chat.get_member(user_id)
            self.cache[chat.id, user_id] = datetime.now(), chat_member
            return chat_member

    def _remove_from_cache_if_expired(self, chat_id: int,
                                      user_id: int) -> None:
        """Removes from cache if the cached value has expired"""
        timestamp, _ = self.cache[chat_id, user_id]
        if timestamp + self.time_to_live < datetime.now():
            del self.cache[chat_id, user_id]


get_cached_chat_member = _GetCachedChatMember()
