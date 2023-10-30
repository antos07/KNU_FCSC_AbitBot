from datetime import date, time, datetime
from typing import Annotated

from sqlalchemy import BigInteger, String, ForeignKey, func
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
)

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
    __tablename__ = "chats"

    # Mapped attributes
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=False)
    """The id of a telegram chat"""
    title: Mapped[str] = mapped_column(String(MAX_TITLE_LENGTH))
    """A current chat title. Not longer than :attr:`MAX_TITLE_LENGTH`."""
    description: Mapped[str]
    """A current description of the chat"""
    invite_link: Mapped[Url]
    """An invite link for this chat."""


class ApplicantChat(Base):
    """Stores applicant chat info"""

    # Dunder vars
    __tablename__ = "applicant_chats"

    # Mapped attributes
    chat_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(Chat.id, ondelete="CASCADE"),
        primary_key=True,
        autoincrement=False,
    )
    """The id of the chat"""
    flood_chat_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("flood_chats." "chat_id")
    )
    """The id of a related flood chat"""
    greet_new_members: Mapped[bool] = mapped_column(default=False)
    """Flag for displaying greetings. Defaults to False"""
    active: Mapped[bool] = mapped_column(default=False)
    """Flag for validating that the applicant chat is active. Defaults to 
    False."""

    # Relationships
    chat: Mapped[Chat] = relationship()
    """An instance of related telegram chat"""
    flood_chat: Mapped["FloodChat"] = relationship()
    """An instance of related flood chat"""
    admission_committee_timetable: Mapped[
        list["AdmissionCommitteeTimetableRecord"]
    ] = relationship(back_populates="applicant_chat")
    """The timetable of the admission committe"""
    required_documents: Mapped[list["RequiredDocument"]] = relationship(
        back_populates="applicant_chat"
    )


class FloodChat(Base):
    """Stores flood chat related data"""

    # Dunder attributes
    __tablename__ = "flood_chats"

    # Mapped attributes
    chat_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(Chat.id, ondelete="CASCADE"),
        primary_key=True,
        autoincrement=False,
    )
    """The id of the telegram chat"""

    # TODO: Introduce more attributes

    # Relationships:
    chat: Mapped[Chat] = relationship()
    """An instance of related telegram chat"""


class AdmissionCommitteeTimetableRecord(Base):
    """Represent records in the admission committe timetable"""

    # Dunder attributes
    __tablename__ = "admission_committee_timetable"

    # Mapped attributes
    applicant_chat_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(ApplicantChat.chat_id, ondelete="CASCADE"),
        primary_key=True,
        autoincrement=False,
    )
    """The id of the applicant chat, for which the timetable is displayed."""
    date: Mapped[date]
    """The date of this record"""
    start_time: Mapped[time]
    """The start of working hours on the given day"""
    end_time: Mapped[time]
    """The end of working hours on the given day"""

    # Relationships
    applicant_chat: Mapped[ApplicantChat] = relationship(
        back_populates="admission_committee_timetable",
    )


class ApplicantDocument(Base):
    """A document needed from applicant"""

    # Dunder attributes
    __tablename__ = "applicant_documents"

    # Constants
    MAX_TITLE_LENGTH: int = 100
    """Max length of a document title"""

    # Mapped attributes
    id: Mapped[int] = mapped_column(primary_key=True)
    """An autogenerated id of the document"""
    title: Mapped[str] = mapped_column(String(MAX_TITLE_LENGTH))
    """A document title. Not longer than :attr:`MAX_MAX_TITLE_LENGTH`"""
    description: Mapped[str | None]
    """A document description"""


class RequiredDocument(Base):
    """Tells that the document is required for applicant chat"""

    # Dunder attributes
    __tablename__ = "required_documents"

    # Mapped attributes
    document_id: Mapped[int] = mapped_column(
        ForeignKey(ApplicantDocument.id, ondelete="CASCADE"), primary_key=True
    )
    """A document id"""
    applicant_chat_id: Mapped[int] = mapped_column(
        ForeignKey(ApplicantChat.chat_id, ondelete="CASCADE"), primary_key=True
    )
    """A chat id"""
    added_at: Mapped[datetime] = mapped_column(insert_default=func.now)
    """Timestamp that shows when the document was added. Autogenerated on
     insert"""
    optional: Mapped[bool]
    """Flag that shows if document is always required"""

    # Relationships:
    document: Mapped[ApplicantDocument] = relationship()
    """A related document"""
    applicant_chat: Mapped[ApplicantChat] = relationship(
        back_populates="required_documents"
    )
    """A related applicant chat"""
