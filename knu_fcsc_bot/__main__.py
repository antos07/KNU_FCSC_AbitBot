import os

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from telegram.constants import ParseMode, UpdateType
from telegram.ext import ApplicationBuilder, Defaults

from knu_fcsc_bot.bot.handlers import setup_handlers


def main():
    app = (ApplicationBuilder()
           .token(os.environ['BOT_TOKEN'])
           .get_updates_http_version('2')
           .http_version('2')
           .defaults(Defaults(parse_mode=ParseMode.HTML))
           .build())
    setup_handlers(app)

    engine = create_async_engine(url=os.environ['DATABASE_URL'])
    sessionmaker = async_sessionmaker(bind=engine, expire_on_commit=False)
    app.bot_data['AsyncSession'] = sessionmaker

    allowed_updates = [
        UpdateType.CHAT_MEMBER,
        UpdateType.CALLBACK_QUERY,
        UpdateType.MESSAGE,
    ]
    app.run_polling(allowed_updates=allowed_updates)


if __name__ == '__main__':
    main()
