#(©)CodeXBotz

import os
import asyncio
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated

from bot import Bot
from config import ADMINS, FORCE_MSG, START_MSG, CUSTOM_CAPTION, DISABLE_CHANNEL_BUTTON, PROTECT_CONTENT, START_PIC, AUTO_DELETE_TIME, AUTO_DELETE_MSG, JOIN_REQUEST_ENABLE, FORCE_SUB_CHANNELS
from helper_func import subscribed, decode, get_messages, delete_file
from database.database import add_user, del_user, full_userbase, present_user


@Bot.on_message(filters.command('start') & filters.private & subscribed)
async def start_command(client: Client, message: Message):

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
            try:
                start = int(int(argument[1]) / abs(client.db_channel.id))
                end = int(int(argument[2]) / abs(client.db_channel.id))
            except:
                return

            if start <= end:
                ids = range(start, end+1)
            else:
                ids = []
                i = start
                while True:
                    ids.append(i)
                    i -= 1
                    if i < end:
                        break

        elif len(argument) == 2:
            try:
                ids = [int(int(argument[1]) / abs(client.db_channel.id))]
            except:
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

            if bool(CUSTOM_CAPTION) and msg.document:
                caption = CUSTOM_CAPTION.format(
                    previouscaption="" if not msg.caption else msg.caption.html,
                    filename=msg.document.file_name
                )
            else:
                caption = "" if not msg.caption else msg.caption.html

            try:
                file_id = None

                if msg.document:
                    file_id = msg.document.file_id
                elif msg.video:
                    file_id = msg.video.file_id
                elif msg.audio:
                    file_id = msg.audio.file_id
                elif msg.photo:
                    file_id = msg.photo.file_id[-1].file_id
                elif msg.animation:
                    file_id = msg.animation.file_id
                elif msg.voice:
                    file_id = msg.voice.file_id

                if file_id:
                    sent = await client.send_cached_media(
                        chat_id=user_id,
                        file_id=file_id,
                        caption=caption,
                        parse_mode=ParseMode.HTML,
                        protect_content=PROTECT_CONTENT
                    )
                else:
                    sent = await msg.copy(chat_id=user_id)

                if AUTO_DELETE_TIME and AUTO_DELETE_TIME > 0 and sent:
                    track_msgs.append(sent)

                await asyncio.sleep(0.5)

            except FloodWait as e:
                await asyncio.sleep(e.value)
            except:
                continue

        if track_msgs:
            delete_data = await client.send_message(
                chat_id=user_id,
                text=AUTO_DELETE_MSG.format(time=AUTO_DELETE_TIME)
            )
            asyncio.create_task(delete_file(track_msgs, client, delete_data))

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


# 🔒 NOT JOINED (PRIVATE FORCE SUB SAFE)
@Bot.on_message(filters.command('start') & filters.private)
async def not_joined(client: Client, message: Message):

    if bool(JOIN_REQUEST_ENABLE):
        invite = await client.create_chat_invite_link(
            chat_id=FORCE_SUB_CHANNELS[0],
            creates_join_request=True
        )
        ButtonUrl = invite.invite_link
    else:
        ButtonUrl = client.invitelink

    buttons = [[InlineKeyboardButton("Join Channel", url=ButtonUrl)]]

    try:
        buttons.append(
            [InlineKeyboardButton("Try Again", url=f"https://t.me/{client.username}?start={message.command[1]}")]
        )
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


# 👥 USERS
@Bot.on_message(filters.command('users') & filters.private & filters.user(ADMINS))
async def get_users(client: Bot, message: Message):
    users = await full_userbase()
    await message.reply(f"{len(users)} users are using this bot")
