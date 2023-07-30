from knu_fcsc_bot.models import AbitChatInfo, UsefulLink, Program


class Error(Exception):
    """Base exception class for this module"""
    pass


class DoesNotExist(Error):
    """Requested object does not exist"""


def _get_chat_info(chat_id: int) -> AbitChatInfo:
    return AbitChatInfo(
        chat_id=chat_id,
        flood_chat_link='https://t.me/+BvDQgzxq6jViOTYy',
        useful_links=[
            UsefulLink(title='📚 ПРАВИЛА ПРИЙОМУ', url='https://vstup.knu.ua/images/2023/%D0%9F%D1%80%D0%B0%D0%B2%D0%B8%D0%BB%D0%B0_%D0%BF%D1%80%D0%B8%D0%B9%D0%BE%D0%BC%D1%8318.07.pdf'),
            UsefulLink(title='📝 ПРИКЛАД МОТИВАЦІЙНОГО', url='https://t.me/knu_vstup/1370'),
            UsefulLink(title='⚙️ Гайд', url='https://telegra.ph/Gajdi-z%D1%96-spec%D1%96alnostej-FKNK-06-10-3'),
            UsefulLink(title='💻 Сайт ФКНК', url='https://csc.knu.ua/uk/'),
            UsefulLink(title='🖥 Поселення в гуртожиток', url='https://t.me/shevadorm16/1147'),
            UsefulLink(title='🏢 ТГ-канал ФКНК', url='https://t.me/cyberknu'),
            UsefulLink(title='🧙🏻‍♀️ Академ мобільність', url='https://t.me/cyber_mobility'),
            UsefulLink(title='🚗 Вакансії', url='https://t.me/cybervacancies'),
        ],
        programs=[
            Program(id=1, title='🔹Прикладна математика (113)', guide_url='https://telegra.ph/Gajd-na-spec%D1%96aln%D1%96st-113-Prikladna-matematika-06-03'),
            Program(id=2, title='🔸Програмна інженерія (121)', guide_url='https://telegra.ph/Gajd-na-spec%D1%96aln%D1%96st-121-%D0%86nzhener%D1%96ya-programnogo-zabezpechennya-05-22-2'),
            Program(id=3, title="🔹Комп'ютерні науки (122)", guide_url='https://telegra.ph/Gajd-na-spec%D1%96aln%D1%96st-122-Kompyutern%D1%96-nauki-06-04'),
            Program(id=4, title='🔸Системний аналіз (124)', guide_url='https://telegra.ph/Vse-shcho-vam-treba-znati-pro-Sistemnij-anal%D1%96z-06-01'),
        ],
    )


async def get_main_abit_chat_info_usecase(chat_id: int) -> AbitChatInfo:
    """Returns main info for given chat_id (useful_links and programs
    are not guarantied)"""
    return _get_chat_info(chat_id)


async def list_programs_usecase(chat_id: int) -> list[Program]:
    """Lists all available programs for the chat"""
    return _get_chat_info(chat_id).programs


async def get_program_by_id_usecase(program_id: int) -> Program:
    """Gets program by its id"""
    info = _get_chat_info(None)
    for program in info.programs:
        if program.id == program_id:
            return program
    raise


async def list_useful_links_usecase(chat_id: int) -> list[UsefulLink]:
    """Lists the useful links for the given chat"""
    return _get_chat_info(chat_id).useful_links
