from motor.motor_asyncio import AsyncIOMotorClient

mongo_client = AsyncIOMotorClient(
    'mongodb+srv://Levs192:pas12345@cluster0.qyfuqkk.mongodb.net/DB_USERS?retryWrites=true&w=majority')
mongo_db = mongo_client['DB_USERS']
users_collection = mongo_db['Collection_USERS']