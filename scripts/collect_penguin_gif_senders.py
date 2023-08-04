import asyncio
import os
from datetime import datetime
from typing import AsyncIterable

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from telethon import TelegramClient
from telethon.types import Chat, Channel, Message, InputMessagesFilterGif

from knu_fcsc_bot import usecases

TARGET_CHAT = 'https://t.me/abit_cyber_2023'
PENGUIN_GIF_FILE_ID = 5955083271002914943
SESSION_NAME = 'antos07'


async def iter_penguin_gif_messages(
        client: TelegramClient,
        chat: Chat | Channel,
) -> AsyncIterable[Message]:
    """A generator that iters through all messages with the pinguin
     gif in the given chat"""
    async for message in client.iter_messages(chat,
                                              filter=InputMessagesFilterGif):
        if message.gif.id == PENGUIN_GIF_FILE_ID:
            logger.debug(f'Found message {message.to_json()}')
            yield message


async def record_penguin_gif(session: AsyncSession, chat_id: int, user_id: int,
                             timestamp: datetime) -> None:
    """Records a penguin gif"""
    logger.debug(f'Recording gif {chat_id=}, {user_id=}, {timestamp=}')
    await usecases.record_chat_member(
        session=session,
        chat_id=chat_id,
        user_id=user_id,
    )
    await usecases.record_penguin_gif_usecase(
        session=session,
        user_id=user_id,
        chat_id=chat_id,
        timestamp=timestamp,
    )
    logger.info(f'Recorded gif {chat_id=}, {user_id=}, {timestamp=}')


async def collect_penguin_gifs(client: TelegramClient,
                               session: AsyncSession,
                               chat: Chat | Channel) -> None:
    """Collects all penguin gifs in the chat"""

    async for message in iter_penguin_gif_messages(client, chat):
        chat_id = chat.id
        if isinstance(chat, Channel):
            chat_id = int(f'-100{chat_id}')
        await record_penguin_gif(
            session=session,
            chat_id=chat_id,
            user_id=message.from_id.user_id,
            timestamp=message.date,
        )


async def main():
    engine = create_async_engine(os.environ['DATABASE_URL'])
    client = TelegramClient(
        session=SESSION_NAME,
        api_id=int(os.environ['API_ID']),
        api_hash=os.environ['API_HASH'],
    )

    with logger.catch():
        async with client, AsyncSession(bind=engine) as session:
            chat = await client.get_entity(TARGET_CHAT)

            await collect_penguin_gifs(client, session, chat)

            await session.commit()


if __name__ == '__main__':
    asyncio.run(main())
