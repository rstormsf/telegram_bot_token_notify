from pprint import pprint
import json
from urllib.parse import quote
from urllib3 import PoolManager
import certifi


def build_txlist_url(address, page, start_block):
    return 'https://api.trustwalletapp.com/transactions?address=%s&page=%s&startBlock=%s' % (
        quote(address),
        str(int(page)),
        str(int(start_block)),
    )


def find_op(recp_address, token_address, start_block=0):
    """
    Find token transfers of `token_address` token to `recp_address` recipient
    """

    pool = PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())
    page = 1
    while True:
        url = build_txlist_url(recp_address, page, start_block)
        print('url', url)
        res = pool.request('GET', url, retries=3)
        data = json.loads(res.data.decode('utf-8'))
        for tx in data['docs']:
            if tx['to'] == token_address: 
                for op in tx['operations']:
                    if op['to'] == recp_address:
                        yield tx, op
        break
