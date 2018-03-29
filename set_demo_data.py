import logging

from project.database import connect_db
from process_ops import setup_logging
from gambit_bot import GambitBot

def main():
    setup_logging()
    db = connect_db()
    wallet_address = '0x0039f22efb07a647557c7c5d17854cfd6d489ef3'
    token_address = '0x6422b80dc6fcb795402f17ad347d8ad31e4ad0a6'
    channel_id = -1001263856479 # gambit-test 

    bot = GambitBot()
    bot.set_setting('wallet', wallet_address)
    bot.set_setting('token', token_address)
    bot.set_setting('channel', channel_id)
    logging.debug('Config has set. Config is:')
    logging.debug(bot.get_settings())


if __name__ == '__main__':
    main()
