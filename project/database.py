import os
from pymongo import MongoClient


def connect_db():
    db = MongoClient(host=os.environ['MONGODB_URI']).get_database()
    db.op.create_index([('_tx.blockNumber', -1)])
    return db
