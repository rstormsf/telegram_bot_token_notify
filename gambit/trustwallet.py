from pprint import pprint
import json
from urllib.parse import quote
import os

import certifi
from urllib3 import PoolManager


def build_txlist_url(address, page, start_block):
    api_url = os.getenv('TRUSTWALLET_API_URL')
    return api_url % {
        'wallet': quote(address),
        'page': int(page),
        'start_block': int(start_block),
    }


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
