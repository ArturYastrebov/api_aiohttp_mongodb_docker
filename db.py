from motor.motor_asyncio import AsyncIOMotorClient

mongo_client = AsyncIOMotorClient(
    "mongodb+srv://Levs192:pas12345@cluster0.qyfuqkk.mongodb.net/DB_USERS?retryWrites=true&w=majority",
    serverSelectionTimeoutMS=60000,
    connect=False,
)
mongo_db = mongo_client["DB_USERS"]
users_collection = mongo_db["Collection_USERS"]
