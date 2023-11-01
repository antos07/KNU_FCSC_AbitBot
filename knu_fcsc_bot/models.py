from datetime import date, time, datetime
from typing import Annotated, Any

from sqlalchemy import (
    BigInteger,
    String,
    ForeignKey,
    func,
    Table,
    Column,
    JSON,
)
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

    # Relationships
    members: Mapped[list["ChatMemeber"]] = relationship(back_populates="chat")


applicant_chat_programs_table = Table(
    "applicant_chat_programs",
    Base.metadata,
    Column(
        "program_id", ForeignKey("programs.id", ondelete="CASCADE"), primary_key=True
    ),
    Column(
        "applicant_chat_id",
        ForeignKey("applicant_chats.chat_id", ondelete="CASCADE"),
        primary_key=True,
    ),
)
"""A row association table for many-to-many relationship between 
:class:`ApplicantChat` and :class:`Program`"""


applicant_chat_useful_links_table = Table(
    "applicant_chat_useful_links",
    Base.metadata,
    Column(
        "link_id", ForeignKey("useful_links.id", ondelete="CASCADE"), primary_key=True
    ),
    Column(
        "applicant_chat_id",
        ForeignKey("applicant_chats.chat_id", ondelete="CASCADE"),
        primary_key=True,
    ),
)
"""A row association table for many-to-many relationship between 
:class:`ApplicantChat` and :class:`UsefulLink`"""


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
    """A list of required documents"""
    programs: Mapped[list["Program"]] = relationship(
        secondary=applicant_chat_programs_table
    )
    """A list of proposed programs"""
    useful_links: Mapped[list["UsefulLink"]] = relationship(
        secondary=applicant_chat_useful_links_table
    )
    """A list of useful links"""


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
    id: Mapped[int] = mapped_column(primary_key=True)
    """A record id"""
    applicant_chat_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(ApplicantChat.chat_id, ondelete="CASCADE"),
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


class Program(Base):
    """Information about a program"""

    # Dunder attributes
    __tablename__ = "programs"

    # Constants
    MAX_TITLE_LENGTH: int = 50
    """Max length of a program title"""

    # Mapped attributes
    id: Mapped[int] = mapped_column(primary_key=True)
    """An autogenerated id of the program"""
    title: Mapped[str] = mapped_column(String(MAX_TITLE_LENGTH))
    """A program title. Not longer than :attr:`MAX_TITLE_LENGTH`"""
    first_year: Mapped[int]
    """The first year when the program became available"""
    description: Mapped[str]
    """A program description"""
    subject_list_url: Mapped[Url]
    """A link to the subject list"""


class UsefulLink(Base):
    """A useful link"""

    # Dunder attributes
    __tablename__ = "useful_links"

    # Constants
    MAX_TITLE_LENGTH: int = 256
    """Max length of a link title"""

    # Mapped attributes
    id: Mapped[int] = mapped_column(primary_key=True)
    """An autogenerated id of the link"""
    title: Mapped[str] = mapped_column(String(MAX_TITLE_LENGTH))
    """A link title. Not longer than :attr:`MAX_TITLE_LENGTH`"""
    url: Mapped[Url]
    """An actual url"""


class User(Base):
    """A telegram user"""

    # Dunder attributes
    __tablename__ = "users"

    # Constants
    MAX_NAME_LENGTH: int = 256
    """Max allowed length of :attr:`first_name` and :attr:`last_name` attributes"""

    # Mapped attributes
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=False)
    """The telegram id of a user"""
    first_name: Mapped[str] = mapped_column(String(MAX_NAME_LENGTH))
    """The user first name. Not longer than :attr:`MAX_NAME_LENGTH`"""
    last_name: Mapped[str | None] = mapped_column(String(MAX_NAME_LENGTH))
    """Optional. The user last name. Not longer than :attr:`MAX_NAME_LENGTH`"""
    username: Mapped[str | None] = mapped_column(String(MAX_NAME_LENGTH))
    """Optional. Thu username. Not longer than :attr:`MAX_NAME_LENGTH`."""

    # Relationship
    memberships: Mapped[list["ChatMemeber"]] = relationship(back_populates="user")


class ChatMemeber(Base):
    """A telegram chat member"""

    # Dunder attributes.
    __tablename__ = "chat_members"

    # Mapped attributes
    chat_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey(Chat.id), primary_key=True, autoincrement=False
    )
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey(User.id), primary_key=True, autoincrement=False
    )
    joined: Mapped[datetime]
    role_id: Mapped[int] = mapped_column(ForeignKey("chat_roles.id"))

    # Relationships
    user: Mapped[User] = relationship(back_populates="memberships")
    chat: Mapped[Chat] = relationship(back_populates="members")
    role: Mapped["ChatRole"] = relationship()


class ChatRole(Base):
    """A role in chat"""

    __tablename__ = "chat_roles"

    # Constants
    MAX_NAME_LENGTH: int = 30

    # Mapped attributes
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(MAX_NAME_LENGTH))


class ChatMemeberLimitation(Base):
    __tablename__ = "chat_member_limitations"

    # Mapped attributes
    id: Mapped[int] = mapped_column(primary_key=True)
    chat_id: Mapped[int] = mapped_column(BigInteger, ForeignKey(Chat.id))
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey(User.id))
    start: Mapped[datetime]
    end: Mapped[datetime | None]
    type_id: Mapped[int] = mapped_column(ForeignKey("chat_member_limitation_types.id"))

    # Relationships
    user: Mapped[User] = relationship(back_populates="memberships")
    chat: Mapped[Chat] = relationship(back_populates="members")
    role: Mapped["ChatMemeberLimitationType"] = relationship()


class ChatMemeberLimitationType(Base):
    __tablename__ = "chat_member_limitation_types"

    # Constants
    MAX_NAME_LENGTH: int = 10

    # Mapped attributes
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(MAX_NAME_LENGTH))


class Message(Base):
    __tablename__ = "messages"

    # Mapped attributes
    message_id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=False
    )
    chat_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey(Chat.id), primary_key=True, autoincrement=False
    )
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey(User.id))
    sent_at: Mapped[datetime]
    last_edit_at: Mapped[datetime]
    content: Mapped[dict[str, Any]] = mapped_column(JSON)


class WebAdmin(Base):
    __tablename__ = "admins"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(100))
    password_hash: Mapped[str] = mapped_column(String(256))
    can_edit_admins: Mapped[bool]
