import typing
from contextlib import suppress
from datetime import timedelta
from functools import wraps
from typing import Callable, Any, TypeAlias

from loguru import logger
from telegram import ChatMemberUpdated, ChatMember, Message, Update
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
        if with_reply_to:
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
    )
    logger.debug(f'Scheduled {message} for deletion at {job.next_t}')


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
            schedule_message_deletion(job_queue, message, delete_after)

            return await wrapped(update, context)

        return wrapper

    return decorator
