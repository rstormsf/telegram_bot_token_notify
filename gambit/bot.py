import json

from telegram import Bot


def load_token():
    with open('var/config.json') as inp:
        data = json.load(inp)
    return data['api_token_production']


def init_bot(token):
    return Bot(token=token)
