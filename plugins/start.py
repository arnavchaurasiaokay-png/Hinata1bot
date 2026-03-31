#(©)CodeXBotz

import os
import asyncio
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated, UserNotParticipant

from bot import Bot
from config import ADMINS, FORCE_MSG, START_MSG, CUSTOM_CAPTION, DISABLE_CHANNEL_BUTTON, PROTECT_CONTENT, START_PIC, AUTO_DELETE_TIME, AUTO_DELETE_MSG, JOIN_REQUEST_ENABLE, FORCE_SUB_CHANNELS
from helper_func import decode, get_messages, delete_file
from database.database import add_user, del_user, full_userbase, present_user
from pyrogram.errors import UserNotParticipant

async def is_joined(client, user_id):
    try:
        for ch in FORCE_SUB_CHANNELS:
            member = await client.get_chat_member(ch, user_id)

            if member.status in ["left", "kicked"]:
                return False

        return True

    except UserNotParticipant:
        return False

    except:
        return True

@Bot.on_message(filters.command('start') & filters.private)
async def start_command(client: Client, message: Message):

    id = message.from_user.id

    # 🔥 FORCE SUB CHECK (ADDED ONLY)
    if FORCE_SUB_CHANNELS:
        joined = await is_joined(client, id)

        if not joined:

            if bool(JOIN_REQUEST_ENABLE):
                invite = await client.create_chat_invite_link(
                    chat_id=FORCE_SUB_CHANNELS[0],
                    creates_join_request=True
                )
                link = invite.invite_link
            else:
                link = client.invitelink

            return await message.reply(
                "🚫 पहले channel join करो फिर file access मिलेगा",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("📢 Join Channel", url=link)]
                ])
            )

    # 👇 REST CODE SAME (UNCHANGED)
    if not await present_user(id):
        try:
            await add_user(id)
        except:
            pass

    text = message.text

    if len(text)>7:
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
                ids = range(start,end+1)
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

            if AUTO_DELETE_TIME and AUTO_DELETE_TIME > 0:

                try:
                    sent = await client.send_cached_media(
                        chat_id=id,
                        file_id=msg.file_id,
                        caption=caption,
                        parse_mode=ParseMode.HTML,
                        protect_content=PROTECT_CONTENT
                    )
                    if sent:
                        track_msgs.append(sent)

                except FloodWait as e:
                    await asyncio.sleep(e.value)

                except:
                    continue

            else:
                try:
                    await client.send_cached_media(
                        chat_id=id,
                        file_id=msg.file_id,
                        caption=caption,
                        parse_mode=ParseMode.HTML,
                        protect_content=PROTECT_CONTENT
                    )
                    await asyncio.sleep(0.5)

                except FloodWait as e:
                    await asyncio.sleep(e.value)

                except:
                    continue

        if track_msgs:
            delete_data = await client.send_message(
                chat_id=id,
                text=AUTO_DELETE_MSG.format(time=AUTO_DELETE_TIME)
            )
            asyncio.create_task(delete_file(track_msgs, client, delete_data))

        return

    else:
        reply_markup = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("😊 About Me", callback_data = "about"),
                    InlineKeyboardButton("🔒 Close", callback_data = "close")
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
