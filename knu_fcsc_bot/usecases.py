from datetime import datetime
from typing import cast, NamedTuple

from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from knu_fcsc_bot.models import (AbitChatInfo, UsefulLink, Program, ChatMember,
                                 SentPinguinRecord, )


class Error(Exception):
    """Base exception class for this module"""
    pass


class DoesNotExist(Error):
    """Requested object does not exist"""


async def get_main_abit_chat_info_usecase(session: AsyncSession,
                                          chat_id: int) -> AbitChatInfo:
    """Returns main info for given chat_id (useful_links and programs
    are not guarantied)"""
    abit_chat_info = cast(AbitChatInfo,
                          await session.get(AbitChatInfo, chat_id))
    if not abit_chat_info:
        raise DoesNotExist
    return abit_chat_info


async def list_programs_usecase(session: AsyncSession,
                                chat_id: int) -> list[Program]:
    """Lists all available programs for the chat"""
    stmt = select(Program).where(Program.chat_id == chat_id)
    return list((await session.scalars(stmt)).all())


async def get_program_by_id_usecase(session: AsyncSession,
                                    program_id: int) -> Program:
    """Gets program by its id"""
    program = cast(Program,
                   await session.get(Program, program_id))
    if not program:
        raise DoesNotExist
    return program


async def list_useful_links_usecase(session: AsyncSession,
                                    chat_id: int) -> list[UsefulLink]:
    """Lists the useful links for the given chat"""
    stmt = select(UsefulLink).where(UsefulLink.chat_id == chat_id)
    return list((await session.scalars(stmt)).all())


async def list_allowed_chat_ids_usecase(session: AsyncSession) -> list[int]:
    """Lists all allowed chat ids"""
    stmt = select(AbitChatInfo.chat_id)
    scalar_results = await session.scalars(stmt)
    return list(scalar_results)


async def record_pinguin_gif_usecase(session: AsyncSession, user_id: int,
                                     chat_id: int,
                                     timestamp: datetime) -> None:
    """Records that user has sent the pinguin gif in chat"""
    chat_member_stmt = select(ChatMember).where(ChatMember.user_id == user_id,
                                                ChatMember.chat_id == chat_id)
    chat_member = await session.scalar(chat_member_stmt)
    pinguin_record = SentPinguinRecord(
        chat_member=chat_member,
        timestamp=timestamp,
    )
    session.add(pinguin_record)


async def record_chat_member(session: AsyncSession, user_id: int,
                             chat_id: int) -> None:
    """Records that the user is a member of the chat"""
    chat = await session.get(AbitChatInfo, chat_id)
    if not chat:
        raise DoesNotExist('No chat with the given id')
    chat_member_stmt = select(ChatMember).where(ChatMember.user_id == user_id,
                                                ChatMember.abit_chat == chat)
    chat_member = await session.scalar(chat_member_stmt)
    if chat_member:
        # The user has been already recorded as the chat member
        return
    chat_member = ChatMember(user_id=user_id, abit_chat=chat)
    session.add(chat_member)


class UserPenguinCount(NamedTuple):
    """The number of penguins sent by a user with user_id"""
    user_id: int
    penguin_count: int


async def top_users_with_most_sent_penguins_usecase(
        session: AsyncSession,
        chat_id: int,
        number: int = 10,
        since: datetime | None = None,
        until: datetime | None = None,
) -> list[UserPenguinCount]:
    """
    Returns top users with the most sent penguins in given chat.

    If number is not specified, returns the Top 10.

    If since is not specified, counts from the beginning of the time.

    If until is not specified, counts till now.
    """
    # Joining ChatMember.pinguins, so to count pinguins its enough
    # to count user_id entries, as there will be an entry for every
    # SentPinguinRecord.
    penguin_count = func.count(ChatMember.user_id).label('penguin_count')
    stmt = (
        select(ChatMember.user_id, penguin_count)
        .where(ChatMember.chat_id == chat_id)
        .join(ChatMember.pinguins)
        .group_by(ChatMember.user_id)
        .order_by(desc(penguin_count))
        .limit(number)
    )
    if since:
        stmt = stmt.where(SentPinguinRecord.timestamp >= since)
    if until:
        stmt = stmt.where(SentPinguinRecord.timestamp <= until)

    results = await session.execute(stmt)

    return [
        UserPenguinCount(user_id, penguin_count)
        for user_id, penguin_count in results.tuples()
    ]
