from typing import Annotated

from sqlalchemy import BigInteger, String, ForeignKey
from sqlalchemy.orm import (DeclarativeBase, Mapped, mapped_column,
                            relationship, )

MAX_URL_LENGTH: int = 500
"""The max allowed length of url"""

Url = Annotated[str, mapped_column(String(MAX_URL_LENGTH))]
"""A shortcut for mapped url"""


class Base(DeclarativeBase):
    """A base class for all models"""


class Chat(Base):
    """Telegram chat data"""

    # Constants:
    MAX_TITLE_LENGTH: int = 256
    """The maximal allowed length of the title"""

    # Dunder vars
    __tablename__ = 'chats'

    # Mapped attributes
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True,
                                    autoincrement=False)
    """The id of a telegram chat"""
    title: Mapped[str] = mapped_column(String(MAX_TITLE_LENGTH))
    """A current chat title. Not longer than :attr:`MAX_TITLE_LENGTH`."""
    description: Mapped[str]
    """A current description of the chat"""
    invite_link: Mapped[Url]
    """An invite link for this chat."""


class ApplicantChat:
    """Stores applicant chat info"""

    # Dunder vars
    __tablename__ = 'applicant_chats'

    # Mapped attributes
    chat_id: Mapped[int] = mapped_column(BigInteger,
                                         ForeignKey(Chat.id,
                                                    ondelete='CASCADE'),
                                         primary_key=True, autoincrement=False)
    """The id of the chat"""
    flood_chat_id: Mapped[int] = mapped_column(BigInteger,
                                               ForeignKey('flood_chats.'
                                                          'chat_id'))
    """The id of a related flood chat"""
    greet_new_members: Mapped[bool] = mapped_column(default=False)
    """Flag for displaying greetings. Defaults to False"""
    active: Mapped[bool] = mapped_column(default=False)
    """Flag for validating that the applicant chat is active. Defaults to 
    False."""

    # Relationships
    chat: Mapped[Chat] = relationship()
    """An instance of related telegram chat"""
    flood_chat: Mapped['FloodChat'] = relationship()
    """An instance of related flood chat"""


class FloodChat(Base):
    """Stores flood chat related data"""

    # Dunder attributes
    __tablename__ = 'flood_chats'

    # Mapped attributes
    chat_id: Mapped[int] = mapped_column(BigInteger,
                                         ForeignKey(Chat.id,
                                                    ondelete='CASCADE'),
                                         primary_key=True, autoincrement=False)
    """The id of the telegram chat"""

    # TODO: Introduce more attributes

    # Relationships:
    chat: Mapped[Chat] = relationship()
    """An instance of related telegram chat"""
