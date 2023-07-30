from dataclasses import dataclass, field


@dataclass
class UsefulLink:
    """A useful link in chat"""
    title: str
    url: str


@dataclass
class Program:
    """Information about available program"""
    title: str
    guide_url: str


@dataclass
class AbitChatInfo:
    """Some basic info to be displayed in the abiturient chat"""
    chat_id: int
    flood_chat_link: str
    useful_links: list[UsefulLink] = field(default_factory=list)
    programs: list[Program] = field(default_factory=list)
