from pymongo import MongoClient

from project.settings import MONGODB


def connect_db():
    db = MongoClient(**MONGODB['connection'])[MONGODB['dbname']]
    db.op.create_index([('_tx.blockNumber', -1)])
    return db
