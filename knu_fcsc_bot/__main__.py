import os
from argparse import ArgumentParser
from dataclasses import dataclass

from loguru import logger
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from telegram.constants import ParseMode, UpdateType
from telegram.ext import (ApplicationBuilder, Defaults, AIORateLimiter,
                          Application, )

from knu_fcsc_bot.bot.handlers import setup_handlers
from knu_fcsc_bot.logginig import (redirect_standard_logging_to_loguru,
                                   disable_low_level_logs, set_logging_level, )
from knu_fcsc_bot.usecases import list_allowed_chat_ids_usecase


@dataclass
class StartupOptions:
    """A collection of startup options"""
    verbose_logging: bool = False
    use_webhook: bool = False


def get_startup_options() -> StartupOptions:
    """Parses command line args into StartupOptions"""
    parser = ArgumentParser()
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='If present, enables DEBUG log-level', )
    parser.add_argument('--use-webhook', '-w',
                        action='store_true',
                        help='If present, switches to using webhook instead '
                             'of long polling')

    args = parser.parse_args()
    return StartupOptions(
        verbose_logging=args.verbose,
        use_webhook=args.use_webhook,
    )


async def app_post_init(app: Application) -> None:
    """Called after Application was initialized to perform additional set up.
    Currently, only loads allowed chats from the database"""
    # Set allowed chats
    session = app.bot_data['AsyncSession']()
    async with session:
        allowed_chat_ids = await list_allowed_chat_ids_usecase(session)
    app.bot_data['allowed_chat_filter'].add_chat_ids(allowed_chat_ids)
    logger.info(f'Registered allowed chat ids {allowed_chat_ids}')


def main():
    startup_options = get_startup_options()

    redirect_standard_logging_to_loguru()
    disable_low_level_logs()
    log_lvl = 'INFO' if not startup_options.verbose_logging else 'DEBUG'
    set_logging_level(log_lvl)

    app = (ApplicationBuilder()
           .token(os.environ['BOT_TOKEN'])
           .get_updates_http_version('2')
           .http_version('2')
           .defaults(Defaults(parse_mode=ParseMode.HTML))
           .rate_limiter(AIORateLimiter(max_retries=2))
           .post_init(app_post_init)
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

    if startup_options.use_webhook:
        raise NotImplementedError('Webhooks are not implemented yet')
    app.run_polling(allowed_updates=allowed_updates)


if __name__ == '__main__':
    main()
