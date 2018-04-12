#!/usr/bin/env python
import re
from copy import deepcopy
from pprint import pprint
import logging
from argparse import ArgumentParser
import time

import telegram.error
from telegram import ParseMode

from project.database import connect_db
from gambit.trustwallet import find_op
from gambit_bot import GambitBot

MSG_TEMPLATE = (
    'New Gambit Telegram membershio and/or Tradingview indicators sold. [Value = %(value)s %(symbol)s](https://etherscan.io/tx/%(tx_id)s) from %(from)s'
)


def load_recent_processed_block_id(db):
    try:
        op = db.op.find({}, sort=[('_tx.blockNumber', -1)])[0]
        return op['_tx']['blockNumber']
    except IndexError:
        return 0


def prepare_op_item(tx, op):
    tx_dup = deepcopy(tx)
    op_dup = deepcopy(op)
    del tx_dup['operations']
    op_dup['_tx'] = tx_dup
    op_dup['_orig_id'] = op_dup['_id']
    op_dup['_id'] = '%s-%s' %  (tx_dup['_id'], op['_id'])
    op_dup['_notified'] = False
    return op_dup


def setup_logging():
    logging.basicConfig(level=logging.DEBUG)


def process_cli():
    parser = ArgumentParser()
    parser.add_argument('--mode', default='production')
    opts = parser.parse_args()
    return {
        'mode': opts.mode,
    }


def format_float(val, decimals):
    val = round(val, decimals)
    if '.' in str(val):
        return str(val).rstrip('0').rstrip('.')
    else:
        return str(val)


def main():
    setup_logging()
    opts = process_cli()
    db = connect_db()

    bot = GambitBot(opts=opts)
    tg_bot = bot.init_bot()
    bot.check_settings()

    block_id = 1 + load_recent_processed_block_id(db)
    recp_address = bot.get_setting('wallet')
    token_address = bot.get_setting('token')
    channel_id = bot.get_setting('channel')

    for tx, op in find_op(recp_address, token_address, start_block=block_id):
        op_item = prepare_op_item(tx, op)
        old_item = db.op.find_one({'_id': op_item['_id']})
        if old_item:
            logging.debug('Found duplicate for operation %s' % op_item['_id'])
        if not old_item or not old_item['_notified']:
            db.op.save(op_item)
            tx_id = re.sub(r'-0$', '', op['transactionId'])
            try:
                decimals = op['contract']['decimals']
            except KeyError:
                decimals = 18
            try:
                symbol = op['contract']['symbol']
            except KeyError:
                symbol = ''
            value_norm = format_float(int(op['value']) / (10**decimals), 2)
            msg = MSG_TEMPLATE % {
                'to': op['to'],
                'from': op['from'],
                'value': value_norm,
                'tx_id': tx_id,
                'symbol': symbol,
            }
            logging.debug(msg)
            logging.debug('Notyfing channel #%s about operation #%s' % (
                channel_id, op_item['_id'],
            ))
            try_limit = 3
            for try_count in range(try_limit):
                try:
                    tg_bot.send_message(
                        channel_id,
                        msg,
                        parse_mode=ParseMode.MARKDOWN,
                        disable_web_page_preview=True
                    )
                except telegram.error.TimedOut as ex:
                    if try_count >= (try_limit - 1):
                        raise
                    else:
                        logging.error('[ERROR] %s' % ex)
                        logging.debug('Retrying to send tg message again...')
                else:
                    break

            time.sleep(0.5)
            db.op.find_one_and_update(
                {'_id': op_item['_id']},
                {'$set': {'notified': True}},
            )


if __name__ == '__main__':
    main()
