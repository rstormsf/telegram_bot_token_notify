#!/usr/bin/env python
from argparse import ArgumentParser
import json
import logging
import os
from copy import deepcopy

from project.database import connect_db

from telegram import ParseMode, Bot
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, RegexHandler


HELP = """
*Commands:*

- `/set <wallet|token|channel> <value>` - set config
- `/config` - show config
- `/chatid` - show chat ID
"""


class InvalidCommand(Exception):
    pass


class GambitBot(object):
    def __init__(self, opts=None):
        self.opts = {
            'mode': None,
        }
        self.db = connect_db()
        if opts:
            self.opts = deepcopy(opts)
            self.check_opts_integrity()

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

    def hook_before_polling(self, updater):
        bot = updater.bot
        logging.debug('Bot info: %s' % bot.get_me())

    def run_polling(self):
        updater = self.init_updater(self.get_token())
        self.register_handlers(updater.dispatcher)
        self.hook_before_polling(updater)
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

    def is_user_admin(self, uid):
        return uid == int(os.environ['TG_ADMIN_ID'])

    def handle_set(self, bot, update):
        msg = update.effective_message
        if msg.chat.type != 'private':
            return
        if not self.is_user_admin(msg.from_user.id):
            bot.send_message(msg.chat.id, 'Access denied')
            return
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

    def get_settings(self):
        return {
            'wallet': self.get_setting('wallet'),
            'token': self.get_setting('token'),
            'channel': self.get_setting('channel'),
        }

    def handle_config(self, bot, update):
        msg = update.effective_message
        if msg.chat.type != 'private':
            return
        if not self.is_user_admin(msg.from_user.id):
            bot.send_message(msg.chat.id, 'Access denied')
            return
        ret = (
            '*Config:*\n'
            '- `wallet:` %(wallet)s\n'
            '- `token:` %(token)s\n'
            '- `channel:` %(channel)s'
        ) % self.get_settings()
        bot.send_message(msg.chat.id, ret, parse_mode=ParseMode.MARKDOWN)

    def handle_chatid(self, bot, update):
        msg = update.effective_message
        if not self.is_user_admin(msg.from_user.id):
            bot.send_message(msg.chat.id, 'Access denied')
            return
        ret = 'Chat ID: %d' % msg.chat.id
        bot.send_message(msg.chat.id, ret)

    def register_handlers(self, dispatcher):
        dispatcher.add_handler(CommandHandler(
            ['start', 'help'], self.handle_start_help)
        )
        dispatcher.add_handler(CommandHandler('set', self.handle_set))
        dispatcher.add_handler(CommandHandler('config', self.handle_config))
        dispatcher.add_handler(CommandHandler('chatid', self.handle_chatid))

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
