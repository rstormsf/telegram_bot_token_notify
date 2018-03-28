#!/usr/bin/env python
from copy import deepcopy
from pprint import pprint
import logging
from argparse import ArgumentParser
import time

from project.database import connect_db
from gambit.trustwallet import find_op
from gambit_bot import GambitBot


MSG_TEMPLATE = (
    'Found token transfer to %(to)s from %(from)s, value=%(value)s'
    ', tx-id=%(tx_id)s'
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
    parser.add_argument(
        '-r', '--repeat', action='store_true', default=False,
        help='Activates every 1 minute, run untill process killed'
    )
    opts = parser.parse_args()
    return {
        'mode': opts.mode,
        'repeat': opts.repeat,
    }


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

    while True:
        for tx, op in find_op(recp_address, token_address, start_block=block_id):
            op_item = prepare_op_item(tx, op)
            old_item = db.op.find_one({'_id': op_item['_id']})
            if old_item:
                logging.debug('Found duplicate for operation %s' % op_item['_id'])
            if not old_item or not old_item['_notified']:
                db.op.save(op_item)
                msg = MSG_TPL % {
                    'to': op['to'],
                    'from': op['from'],
                    'value': op['value'],
                    'tx_id': op['transactionId'],
                }
                logging.debug(msg)
                logging.debug('Notyfing channel #%d about operation #%s' % (
                    channel_id, op_item['_id'],
                ))
                tg_bot.send_message(channel_id, msg)
                db.op.find_one_and_update(
                    {'_id': op_item['_id']},
                    {'$set': {'notified': True}},
                )
        if opts['repeat']:
            time.sleep(60)
        else:
            break


if __name__ == '__main__':
    main()
