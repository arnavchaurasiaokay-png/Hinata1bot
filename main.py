from bot import Bot

# 🔹 UptimeRobot ke liye
from keep_alive import keep_alive
keep_alive()

# 🔹 MongoDB keep alive
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

client = AsyncIOMotorClient("YOUR_MONGO_URI")
db = client["your_db"]

async def keep_mongo_alive():
    while True:
        try:
            await db.command("ping")
            print("MongoDB alive")
        except Exception as e:
            print("Mongo error:", e)
        await asyncio.sleep(300)

# 🔹 Bot start + Mongo keep alive
async def main():
    asyncio.create_task(keep_mongo_alive())
    Bot().run()

if __name__ == "__main__":
    asyncio.run(main())
