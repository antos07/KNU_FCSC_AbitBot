from datetime import datetime

from sqlalchemy import String, BigInteger, ForeignKey, Index
from sqlalchemy.orm import (DeclarativeBase, Mapped, mapped_column,
                            relationship, MappedAsDataclass, )

MAX_URL_LENGTH = 500


class Base(MappedAsDataclass, DeclarativeBase):
    """A base class for all models"""


class UsefulLink(Base):
    """A useful link in chat"""
    MAX_TITLE_LENGTH = 50

    __tablename__ = 'useful_links'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True,
                                    init=False)
    title: Mapped[str] = mapped_column(String(MAX_TITLE_LENGTH))
    url: Mapped[str] = mapped_column(String(MAX_URL_LENGTH))

    chat_id: Mapped[int] = mapped_column(BigInteger,
                                         ForeignKey('abit_chat_info'),
                                         default=None)


class Program(Base):
    """Information about available program"""
    MAX_TITLE_LENGTH = 50

    __tablename__ = 'programs'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True,
                                    init=False)
    title: Mapped[str] = mapped_column(String(MAX_TITLE_LENGTH))
    guide_url: Mapped[str] = mapped_column(String(MAX_URL_LENGTH))

    chat_id: Mapped[int] = mapped_column(BigInteger,
                                         ForeignKey('abit_chat_info'),
                                         default=None)


class AbitChatInfo(Base):
    """Some basic info to be displayed in the abiturient chat"""
    MAX_FILE_ID_LENGTH = 100

    __tablename__ = 'abit_chat_info'

    chat_id: Mapped[int] = mapped_column(BigInteger,
                                         primary_key=True, autoincrement=False)
    greeting_photo_file_id: Mapped[str] = mapped_column(
        String(MAX_FILE_ID_LENGTH),
    )
    flood_chat_link: Mapped[str] = mapped_column(String(MAX_URL_LENGTH))
    useful_links: Mapped[list[UsefulLink]] = relationship(
        default_factory=list,
        lazy='raise'
    )
    programs: Mapped[list[Program]] = relationship(
        default_factory=list,
        lazy='raise'
    )


class ChatMember(Base):
    """A member of abit chat"""

    __tablename__ = 'chat_members'

    id: Mapped[int] = mapped_column(primary_key=True, init=False, default=None)
    user_id: Mapped[int] = mapped_column(BigInteger)
    chat_id: Mapped[int] = mapped_column(BigInteger,
                                         ForeignKey('abit_chat_info.chat_id'),
                                         autoincrement=False)

    abit_chat: Mapped[AbitChatInfo] = relationship(lazy='raise')
    pinguins: Mapped[list['SentPinguinRecord']] = relationship(
        lazy=True,
        back_populates='chat_member',
    )

    __table_args__ = (
        Index('ix_chat_members__user_id__chat_id', 'user_id',
              'chat_id', unique=True),
    )


class SentPinguinRecord(Base):
    """Records sent pinguin gifs"""

    __tablename__ = 'sent_pinguin_records'

    id: Mapped[int] = mapped_column(primary_key=True, default=None, init=False)
    timestamp: Mapped[datetime]
    chat_member: Mapped[ChatMember] = relationship(
        lazy=False,
        back_populates='pinguins',
    )

    chat_member_id: Mapped[int] = mapped_column(ForeignKey('chat_members.id'),
                                                default=None)
