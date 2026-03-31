# (©) Codexbotz

from aiohttp import web
from plugins import web_server

import pyromod.listen
from pyrogram import Client
from pyrogram.enums import ParseMode
import sys
from datetime import datetime
import os  # ✅ added

from config import API_HASH, APP_ID, LOGGER, TG_BOT_TOKEN, TG_BOT_WORKERS, FORCE_SUB_CHANNEL, CHANNEL_ID

# ✅ Railway dynamic PORT
PORT = int(os.environ.get("PORT", 8080))


ascii_art = """
░█████╗░░█████╗░██████╗░███████╗██╗░░██╗██████╗░░█████╗░████████╗███████╗
██╔══██╗██╔══██╗██╔══██╗██╔════╝╚██╗██╔╝██╔══██╗██╔══██╗╚══██╔══╝╚════██║
██║░░╚═╝██║░░██║██║░░██║█████╗░░░╚███╔╝░██████╦╝██║░░██║░░░██║░░░░░███╔═╝
██║░░██╗██║░░██║██║░░██║██╔══╝░░░██╔██╗░██╔══██╗██║░░██║░░░██║░░░██╔══╝░░
╚█████╔╝╚█████╔╝██████╔╝███████╗██╔╝╚██╗██████╦╝╚█████╔╝░░░██║░░░███████╗
░╚════╝░░╚════╝░╚═════╝░╚══════╝╚═╝░░╚═╝╚═════╝░░╚════╝░░░░╚═╝░░░╚══════╝
"""


class Bot(Client):
    def __init__(self):
        super().__init__(
            name="Bot",
            api_hash=API_HASH,
            api_id=APP_ID,
            plugins={"root": "plugins"},
            workers=TG_BOT_WORKERS,
            bot_token=TG_BOT_TOKEN
        )
        self.LOGGER = LOGGER

    async def start(self):
        await super().start()
        usr_bot_me = await self.get_me()
        self.uptime = datetime.now()

        # -------- FORCE SUB -------- #
        if FORCE_SUB_CHANNEL:
            try:
                link = (await self.get_chat(FORCE_SUB_CHANNEL)).invite_link
                if not link:
                    await self.export_chat_invite_link(FORCE_SUB_CHANNEL)
                    link = (await self.get_chat(FORCE_SUB_CHANNEL)).invite_link
                self.invitelink = link
            except Exception as a:
                self.LOGGER(__name__).warning(a)
                self.LOGGER(__name__).warning("Bot can't Export Invite link!")
                sys.exit()

        # -------- DB CHANNEL -------- #
        try:
            db_channel = await self.get_chat(CHANNEL_ID)
            self.db_channel = db_channel
            test = await self.send_message(chat_id=db_channel.id, text="Test Message")
            await test.delete()
        except Exception as e:
            self.LOGGER(__name__).warning(e)
            self.LOGGER(__name__).warning("Check CHANNEL_ID / Bot Admin")
            sys.exit()

        self.set_parse_mode(ParseMode.HTML)
        self.LOGGER(__name__).info(f"Bot Running..!\n\nCreated by \nhttps://t.me/CodeXBotz")
        print(ascii_art)
        print("Welcome to CodeXBotz File Sharing Bot")
        self.username = usr_bot_me.username

        # -------- WEB SERVER -------- #
        app = web.AppRunner(await web_server())
        await app.setup()

        bind_address = "0.0.0.0"
        await web.TCPSite(app, bind_address, PORT).start()
        from aiohttp import web
import asyncio
import os

PORT = int(os.environ.get("PORT", 8080))

async def start_web_server():
    app = web.Application()

    async def home(request):
        return web.Response(text="Bot is alive!")

    app.router.add_get("/", home)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()

    print(f"Web server running on port {PORT}")

    # 🔥 IMPORTANT: loop alive rakho
    while True:
        await asyncio.sleep(3600)
        from aiohttp import web
import asyncio
import os

PORT = int(os.environ.get("PORT", 8080))

async def start_web_server():
    app = web.Application()

    async def home(request):
        return web.Response(text="Bot is alive!")

    app.router.add_get("/", home)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()

    print(f"Web server running on port {PORT}")

    # 🔥 IMPORTANT: loop alive rakho
    while True:
        await asyncio.sleep(3600)

    async def stop(self, *args):
        await super().stop()
        self.LOGGER(__name__).info("Bot stopped.")
