#!/usr/bin/env python
from argparse import ArgumentParser
import json
import logging
import os

from project.database import connect_db

from telegram import ParseMode, Bot
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, RegexHandler


HELP = """
# Commands:

`/set <wallet|token|channel> <value>` - set config
`/config` - show config
"""


class InvalidCommand(Exception):
    pass


class GambitBot(object):
    def __init__(self):
        self.opts = {
            'mode': None,
        }
        self.db = connect_db()

    def parse_cli_opts(self):
        parser = ArgumentParser()
        parser.add_argument('--mode', default='production')
        opts = parser.parse_args()
        self.opts = {
            'mode': opts.mode,
        }
        self.check_opts_integrity()

    def get_token(self):
        return os.environ[('tg_api_token_%s' % self.opts['mode']).upper()]

    def run_polling(self):
        updater = self.init_updater(self.get_token())
        self.register_handlers(updater.dispatcher)
        updater.bot.delete_webhook()
        updater.start_polling()

    def init_bot(self, token=None):
        if token is None:
            token = self.get_token()
        return Bot(token=token)

    def check_opts_integrity(self):
        assert self.opts['mode'] in ('production', 'test')

    def init_updater(self, token=None):
        if token is None:
            token = self.get_token()
        return Updater(token=token, workers=16)

    def handle_start_help(self, bot, update):
        msg = update.effective_message
        if msg.chat.type == 'private':
            bot.send_message(
                chat_id=msg.chat.id,
                text=HELP,
                parse_mode=ParseMode.MARKDOWN,
                disable_web_page_preview=True
            )

    def set_setting(self, key, value):
        self.db.setting.find_one_and_update(
            {'_id': key},
            {'$set': {'value': value}},
            upsert=True,
        )

    def get_setting(self, key):
        try:
            return self.db.setting.find_one({'_id': key})['value']
        except TypeError:
            return None

    def handle_set(self, bot, update):
        msg = update.effective_message
        try:
            items = msg.text.strip().split(' ')
            if not len(items) == 3:
                raise InvalidCommand
            setting = items[1]
            value = items[2]
            if not setting in ('wallet', 'token', 'channel'):
                raise InvalidCommand
            self.set_setting(setting, value)
        except InvalidCommand:
            bot.send_message(msg.chat.id, 'Invalid command')
        else:
            bot.send_message(
                msg.chat.id,
                'Setting `%s` has been set to `%s' % (setting, value)
            )

    def handle_config(self, bot, update):
        msg = update.effective_message
        wallet = self.get_setting('wallet') 
        token = self.get_setting('token') 
        channel = self.get_setting('channel') 
        ret = '''# Config:
        * `wallet:` %s
        * `token:` %s
        * `channel:` %s
        ''' % (
            wallet,
            token,
            channel,
        )
        bot.send_message(msg.chat.id, ret)

    def register_handlers(self, dispatcher):
        dispatcher.add_handler(CommandHandler(
            ['start', 'help'], self.handle_start_help)
        )
        dispatcher.add_handler(CommandHandler('set', self.handle_set))
        dispatcher.add_handler(CommandHandler('config', self.handle_config))

    def check_settings(self):
        wallet = self.get_setting('wallet') 
        token = self.get_setting('token') 
        channel = self.get_setting('channel') 
        assert wallet is not None
        assert wallet is not None
        assert channel is not None


def main():
    logging.basicConfig(level=logging.DEBUG)
    bot = GambitBot()
    bot.parse_cli_opts()
    bot.run_polling()


if __name__ == '__main__':
    main()
