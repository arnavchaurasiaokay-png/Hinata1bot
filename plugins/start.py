#(©)CodeXBotz

import asyncio
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait

from bot import Bot
from config import ADMINS, FORCE_MSG, START_MSG, CUSTOM_CAPTION, PROTECT_CONTENT, START_PIC, AUTO_DELETE_TIME, AUTO_DELETE_MSG
from helper_func import check_sub, decode, get_messages, delete_file
from database.database import add_user, full_userbase, present_user


# 🔥 START COMMAND
@Bot.on_message(filters.command('start') & filters.private)
async def start_command(client: Client, message: Message):

    # 🔒 FORCE SUB CHECK (TOP)
    is_joined = await check_sub(None, client, message)

    if not is_joined:
        buttons = []

        for i, link in enumerate(client.invitelinks):
            buttons.append(
                [InlineKeyboardButton(f"📢 Join Channel {i+1}", url=link)]
            )

        buttons.append(
            [InlineKeyboardButton("✅ Verify", callback_data="checksub")]
        )

        await message.reply(
            text="🚫 Please join all channels then click VERIFY",
            reply_markup=InlineKeyboardMarkup(buttons),
            quote=True
        )
        return


    # ✅ USER SAVE
    user_id = message.from_user.id

    if not await present_user(user_id):
        try:
            await add_user(user_id)
        except:
            pass

    text = message.text

    # 🔗 FILE LINK SYSTEM
    if len(text) > 7:
        try:
            base64_string = text.split(" ", 1)[1]
        except:
            return

        string = await decode(base64_string)
        argument = string.split("-")

        if len(argument) == 3:
            start = int(int(argument[1]) / abs(client.db_channel.id))
            end = int(int(argument[2]) / abs(client.db_channel.id))
            ids = range(start, end+1)

        elif len(argument) == 2:
            ids = [int(int(argument[1]) / abs(client.db_channel.id))]

        temp_msg = await message.reply("Please wait...")

        try:
            messages = await get_messages(client, ids)
        except:
            await message.reply_text("Something went wrong..!")
            return

        await temp_msg.delete()

        for msg in messages:
            await msg.copy(
                chat_id=message.from_user.id,
                caption=msg.caption.html if msg.caption else "",
                parse_mode=ParseMode.HTML,
                protect_content=PROTECT_CONTENT
            )

        return


    # 🏠 NORMAL START
    reply_markup = InlineKeyboardMarkup(
        [[
            InlineKeyboardButton("😊 About Me", callback_data="about"),
            InlineKeyboardButton("🔒 Close", callback_data="close")
        ]]
    )

    if START_PIC:
        await message.reply_photo(
            photo=START_PIC,
            caption=START_MSG.format(
                first=message.from_user.first_name,
                last=message.from_user.last_name,
                username='@' + message.from_user.username if message.from_user.username else None,
                mention=message.from_user.mention,
                id=message.from_user.id
            ),
            reply_markup=reply_markup,
            quote=True
        )
    else:
        await message.reply_text(
            text=START_MSG.format(
                first=message.from_user.first_name,
                last=message.from_user.last_name,
                username='@' + message.from_user.username if message.from_user.username else None,
                mention=message.from_user.mention,
                id=message.from_user.id
            ),
            reply_markup=reply_markup,
            quote=True
        )


# 🔥 VERIFY BUTTON
@Bot.on_callback_query(filters.regex("checksub"))
async def verify_sub(client, query):

    is_joined = await check_sub(None, client, query.message)

    if not is_joined:
        await query.answer("❌ You didn't join all channels", show_alert=True)
        return

    await query.answer("✅ Verified! Send /start again", show_alert=True)


# 👥 USERS
@Bot.on_message(filters.command('users') & filters.private & filters.user(ADMINS))
async def get_users(client: Bot, message: Message):
    users = await full_userbase()
    await message.reply(f"{len(users)} users are using this bot")
