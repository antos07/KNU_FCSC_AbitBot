from datetime import datetime
from typing import cast

from sqlalchemy import select
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
