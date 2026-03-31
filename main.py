import asyncio
from bot import Bot

bot = Bot()

async def main():
    await bot.start()
    print("Bot Running...")

    # 🔥 Keep bot alive forever (IMPORTANT)
    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    asyncio.run(main())
