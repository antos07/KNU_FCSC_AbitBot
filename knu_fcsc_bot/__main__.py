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
class WebhookOptions:
    """Sub-options for webhooks setup. Default values are taken from
    Application.start_webhook docs"""
    host: str = "127.0.0.1"
    port: int = 80
    url_path: str = ""
    webhook_url: str = None


@dataclass
class StartupOptions:
    """A collection of startup options"""
    verbose_logging: bool = False

    use_webhook: bool = False
    webhook_options: WebhookOptions = None


def get_startup_options() -> StartupOptions:
    """Parses command line args into StartupOptions"""
    parser = ArgumentParser()
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='If present, enables DEBUG log-level', )
    parser.set_defaults(use_webhook=None)
    subparsers = parser.add_subparsers()

    # Polling options
    polling_parser = subparsers.add_parser('polling', help='Run polling')
    polling_parser.set_defaults(use_webhook=False)

    # Webhook options
    webhook_parser = subparsers.add_parser('webhook', help='Run webhook')
    webhook_parser.set_defaults(use_webhook=True)
    webhook_parser.add_argument('--host', '-l',
                                help='Host to listen',
                                default=WebhookOptions.host)
    webhook_parser.add_argument('--port', '-p', type=int,
                                help='Port to listen',
                                default=WebhookOptions.port)
    webhook_parser.add_argument('--url-path', '-u',
                                help='Url path',
                                default=WebhookOptions.url_path)
    webhook_parser.add_argument('--webhook-url', '-w',
                                help='A url that will be used by Telegram to'
                                     'reference the webhook')

    args = parser.parse_args()
    options = StartupOptions(
        verbose_logging=args.verbose,
        use_webhook=args.use_webhook,
    )
    if options.use_webhook is None:
        # No running option specified. Printing help.
        parser.print_help()
        parser.exit()
    if options.use_webhook:
        options.webhook_options = WebhookOptions(
            host=args.host,
            port=args.port,
            url_path=args.url_path,
            webhook_url=args.webhook_url,
        )
    return options


async def app_post_init(app: Application) -> None:
    """Called after Application was initialized to perform additional set up.
    Currently, only loads allowed chats from the database"""
    # Set allowed chats
    session = app.bot_data['AsyncSession']()
    async with session:
        allowed_chat_ids = await list_allowed_chat_ids_usecase(session)
    app.bot_data['allowed_chat_filter'].add_chat_ids(allowed_chat_ids)
    logger.info(f'Registered allowed chat ids {allowed_chat_ids}')


def setup_sqlalchemy(app: Application) -> None:
    """Setup sqlalchemy"""
    try:
        db_url = os.environ['DATABASE_URL']
    except KeyError:
        raise RuntimeError('Environmental variable "DATABASE_URL" is not set.')
    engine = create_async_engine(url=db_url)
    sessionmaker = async_sessionmaker(bind=engine, expire_on_commit=False)
    app.bot_data['AsyncSession'] = sessionmaker


def main():
    startup_options = get_startup_options()

    redirect_standard_logging_to_loguru()
    disable_low_level_logs()
    log_lvl = 'INFO' if not startup_options.verbose_logging else 'DEBUG'
    set_logging_level(log_lvl)

    app = (ApplicationBuilder()
           .token(os.environ['BOT_TOKEN'])
           # .get_updates_http_version('2')
           # .http_version('2')
           .defaults(Defaults(parse_mode=ParseMode.HTML))
           .rate_limiter(AIORateLimiter(max_retries=2))
           .post_init(app_post_init)
           .build())

    # Give the bot access to startup options
    app.bot_data['startup_options'] = startup_options

    setup_handlers(app)
    setup_sqlalchemy(app)

    # Run bot
    allowed_updates = [
        UpdateType.CHAT_MEMBER,
        UpdateType.CALLBACK_QUERY,
        UpdateType.MESSAGE,
        UpdateType.MY_CHAT_MEMBER,
    ]
    if startup_options.use_webhook:
        # using webhook
        app.run_webhook(
            listen=startup_options.webhook_options.host,
            port=startup_options.webhook_options.port,
            url_path=startup_options.webhook_options.url_path,
            webhook_url=startup_options.webhook_options.webhook_url,
            allowed_updates=allowed_updates,
        )
    else:
        app.run_polling(allowed_updates=allowed_updates)


if __name__ == '__main__':
    main()
