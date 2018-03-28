import logging

from project.database import connect_db
from process_ops import setup_logging
from gambit_bot import GambitBot

def main():
    setup_logging()
    db = connect_db()
    wallet_address = '0xe47494379c1d48ee73454c251a6395fdd4f9eb43' # some recepient
    token_address = '0x12459c951127e0c374ff9105dda097662a027093' # some contract
    channel_id = -1001263856479 # gambit-test 

    bot = GambitBot()
    bot.set_setting('wallet', wallet_address)
    bot.set_setting('token', token_address)
    bot.set_setting('channel', channel_id)
    logging.debug('Config has set. Config is:')
    logging.debug(bot.get_settings())


if __name__ == '__main__':
    main()
