import os

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from knu_fcsc_bot.models import *

engine = create_engine(os.environ['DATABASE_URL'])

with Session(bind=engine) as session:
    info = AbitChatInfo(
        chat_id=int(input('chat_id=')),
        flood_chat_link='https://t.me/+BvDQgzxq6jViOTYy',
        useful_links=[
            UsefulLink(title='📚 ПРАВИЛА ПРИЙОМУ',
                       url='https://vstup.knu.ua/images/2023/%D0%9F%D1%80%D0%B0%D0%B2%D0%B8%D0%BB%D0%B0_%D0%BF%D1%80%D0%B8%D0%B9%D0%BE%D0%BC%D1%8318.07.pdf'),
            UsefulLink(title='📝 ПРИКЛАД МОТИВАЦІЙНОГО',
                       url='https://t.me/knu_vstup/1370'),
            UsefulLink(title='⚙️ Гайд',
                       url='https://telegra.ph/Gajdi-z%D1%96-spec%D1%96alnostej-FKNK-06-10-3'),
            UsefulLink(title='💻 Сайт ФКНК', url='https://csc.knu.ua/uk/'),
            UsefulLink(title='🖥 Поселення в гуртожиток',
                       url='https://t.me/shevadorm16/1147'),
            UsefulLink(title='🏢 ТГ-канал ФКНК', url='https://t.me/cyberknu'),
            UsefulLink(title='🧙🏻‍♀️ Академ мобільність',
                       url='https://t.me/cyber_mobility'),
            UsefulLink(title='🚗 Вакансії', url='https://t.me/cybervacancies'),
        ],
        programs=[
            Program(title='🔹Прикладна математика (113)',
                    guide_url='https://telegra.ph/Gajd-na-spec%D1%96aln%D1%96st-113-Prikladna-matematika-06-03'),
            Program(title='🔸Програмна інженерія (121)',
                    guide_url='https://telegra.ph/Gajd-na-spec%D1%96aln%D1%96st-121-%D0%86nzhener%D1%96ya-programnogo-zabezpechennya-05-22-2'),
            Program(title="🔹Комп'ютерні науки (122)",
                    guide_url='https://telegra.ph/Gajd-na-spec%D1%96aln%D1%96st-122-Kompyutern%D1%96-nauki-06-04'),
            Program(title='🔸Системний аналіз (124)',
                    guide_url='https://telegra.ph/Vse-shcho-vam-treba-znati-pro-Sistemnij-anal%D1%96z-06-01'),
        ],
        greeting_photo_file_id='AgACAgIAAxkBAAIFrmTGyc6UgGhTHiPyLQ5FUJUOfMttAAKUxzEbhjZAS5JoZuST6gOeAQADAgADeQADLwQ'
    )
    session.add(info)
    session.commit()
