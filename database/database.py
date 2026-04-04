import pymongo, os, time
from config import DB_URI, DB_NAME

dbclient = pymongo.MongoClient(DB_URI)
database = dbclient[DB_NAME]

user_data = database['users']
token_data = database['tokens']


async def present_user(user_id: int):
    found = user_data.find_one({'_id': user_id})
    return bool(found)


async def add_user(user_id: int):
    user_data.insert_one({'_id': user_id})
    return


async def full_userbase():
    user_docs = user_data.find()
    user_ids = []
    for doc in user_docs:
        user_ids.append(doc['_id'])
    return user_ids


async def del_user(user_id: int):
    user_data.delete_one({'_id': user_id})
    return


# 🔥 TOKEN SYSTEM
async def save_token(token, user_id):
    token_data.insert_one({
        "token": token,
        "user_id": user_id,
        "time": time.time()
    })


async def get_token(token):
    return token_data.find_one({"token": token})
