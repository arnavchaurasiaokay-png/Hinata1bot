# (©)CodeXBotz

import os
import asyncio
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait

from bot import Bot
from config import ADMINS, FORCE_MSG, START_MSG, CUSTOM_CAPTION, DISABLE_CHANNEL_BUTTON, PROTECT_CONTENT, START_PIC, AUTO_DELETE_TIME, AUTO_DELETE_MSG, JOIN_REQUEST_ENABLE, FORCE_SUB_CHANNEL
from helper_func import subscribed, decode, get_messages, delete_file
from database.database import add_user, del_user, full_userbase, present_user


# 🔥 FIXED START HANDLER (NO AUTO LINK)
@Bot.on_message(filters.command('start') & filters.private & subscribed)
async def start_command(client: Client, message: Message):

    id = message.from_user.id

    # ✅ Add user safely
    if not await present_user(id):
        try:
            await add_user(id)
        except:
            pass

    # 🔥 IMPORTANT FIX → no payload = no link
    if len(message.command) < 2:
        return await send_welcome(client, message)

    # ✅ Payload handling (ONLY when /start xxx)
    try:
        base64_string = message.text.split(" ", 1)[1]
    except:
        return

    try:
        string = await decode(base64_string)
    except:
        return

    argument = string.split("-")

    # 🔹 Get message IDs
    if len(argument) == 3:
        try:
            start = int(int(argument[1]) / abs(client.db_channel.id))
            end = int(int(argument[2]) / abs(client.db_channel.id))
        except:
            return

        ids = range(start, end + 1) if start <= end else list(range(start, end - 1, -1))

    elif len(argument) == 2:
        try:
            ids = [int(int(argument[1]) / abs(client.db_channel.id))]
        except:
            return
    else:
        return

    temp_msg = await message.reply("Please wait...")

    try:
        messages = await get_messages(client, ids)
    except:
        await message.reply_text("Something went wrong..!")
        return

    await temp_msg.delete()

    track_msgs = []

    for msg in messages:

        caption = (
            CUSTOM_CAPTION.format(
                previouscaption="" if not msg.caption else msg.caption.html,
                filename=msg.document.file_name
            )
            if CUSTOM_CAPTION and msg.document
            else ("" if not msg.caption else msg.caption.html)
        )

        try:
            copied = await msg.copy(
                chat_id=message.from_user.id,
                caption=caption,
                parse_mode=ParseMode.HTML,
                protect_content=PROTECT_CONTENT
            )

            if copied:
                track_msgs.append(copied)

            await asyncio.sleep(0.5)

        except FloodWait as e:
            await asyncio.sleep(e.value)
        except:
            pass

    # 🔥 Auto delete (optional)
    if AUTO_DELETE_TIME and track_msgs:
        delete_msg = await client.send_message(
            chat_id=message.from_user.id,
            text=AUTO_DELETE_MSG.format(time=AUTO_DELETE_TIME)
        )
        asyncio.create_task(delete_file(track_msgs, client, delete_msg))


# ✅ CLEAN WELCOME FUNCTION
async def send_welcome(client, message):

    reply_markup = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("😊 About Me", callback_data="about"),
                InlineKeyboardButton("🔒 Close", callback_data="close")
            ]
        ]
    )

    if START_PIC:
        await message.reply_photo(
            photo=START_PIC,
            caption=START_MSG.format(
                first=message.from_user.first_name,
                last=message.from_user.last_name,
                username=None if not message.from_user.username else '@' + message.from_user.username,
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
                username=None if not message.from_user.username else '@' + message.from_user.username,
                mention=message.from_user.mention,
                id=message.from_user.id
            ),
            reply_markup=reply_markup,
            disable_web_page_preview=True,
            quote=True
        )


# ❌ FORCE SUB HANDLER (UNCHANGED)
@Bot.on_message(filters.command('start') & filters.private)
async def not_joined(client: Client, message: Message):

    if bool(JOIN_REQUEST_ENABLE):
        invite = await client.create_chat_invite_link(
            chat_id=FORCE_SUB_CHANNEL,
            creates_join_request=True
        )
        ButtonUrl = invite.invite_link
    else:
        ButtonUrl = client.invitelink

    buttons = [[InlineKeyboardButton("Join Channel", url=ButtonUrl)]]

    try:
        buttons.append([
            InlineKeyboardButton(
                text='Try Again',
                url=f"https://t.me/{client.username}?start={message.command[1]}"
            )
        ])
    except:
        pass

    await message.reply(
        text=FORCE_MSG.format(
            first=message.from_user.first_name,
            last=message.from_user.last_name,
            username=None if not message.from_user.username else '@' + message.from_user.username,
            mention=message.from_user.mention,
            id=message.from_user.id
        ),
        reply_markup=InlineKeyboardMarkup(buttons),
        quote=True
    )
