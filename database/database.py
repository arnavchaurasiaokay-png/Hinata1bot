# (©) CodeXBotz

import pymongo
from config import DB_URI, DB_NAME

# ✅ Mongo Client
dbclient = pymongo.MongoClient(DB_URI)

# ✅ Database
database = dbclient[DB_NAME]

# ✅ Collection
user_data = database['users']


# ---------------- USER FUNCTIONS ---------------- #

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


# ---------------- PING FUNCTION ---------------- #

def ping_db():
    try:
        user_data.count_documents({})
        return True
    except Exception as e:
        print(f"MongoDB Ping Error: {e}")
        return False
