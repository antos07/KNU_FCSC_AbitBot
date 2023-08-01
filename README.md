# KNU-FCSC-AbitBot

This is an info Telegram bot for applicants to Faculty Of 
Computer Science And Cybernetics at Taras Shevchenko National
University of Kyiv.

Available at the applicants [chat](https://t.me/abit_cyber_2023) or
by username @KNU_FCSC_AbitBot.

## Installation

You will need Python 3.11. It was tested using Python 3.11.4, so
I _strongly recommend_ to use it.

This bot is only available on GitHub, so you should clone this 
repository:

    git clone https://github.com/antos07/KNU_FCSC_AbitBot.git

Install the project via 
[Poetry](https://python-poetry.org/) (v. 1.2.2 is used):

    poetry install

Check that everything was set up correctly by running the 
`knu_fcsc_bot` package as a module (this and the following 
examples work for Linux, you should use py3 instead of python3
on Windows)

    python3 -m knu_fcsc_bot

Congrats! You have successfully installed the bot.

## How two run the bot?

There are two supported mods: polling and webhook. Check the
Telegram docs or this [article](https://github.com/python-telegram-bot/python-telegram-bot/wiki/Webhooks) 
for more info about it.

### Polling

This one is simple. You just need to run the following command
to get everything working:

    python3 -m knu_fcsc_bot polling

### Webhook

This requires some preparations (you will need a public IP 
address and ability to accept HTTPS requests). Check the 
[article](https://github.com/python-telegram-bot/python-telegram-bot/wiki/Webhooks)
for more detailed requirements. However, currently certificates 
are not supported, so you have to work behind a reverse-proxy.

The general command for starting webhook is:

    python3 -m knu_fcsc_bot webhook

But you will probably need to use some of the following 
arguments:

- `--host <host>`/`-l <host>` to specify which host to listen. 
Defaults to `127.0.0.1`.
- `--port <port>`/`-p <port>` to specify which port to listen.
Defaults to `80`.
- `--url-path <url_path>`/`-u <url_path>` to specify the url 
path, which the bot will be listening to. Defaults to "".
- `--webhook-url <url>`/`-w <url>` to tell telegram, where to
send updates. If not passed, the bot will try to guess it from 
other parameters,