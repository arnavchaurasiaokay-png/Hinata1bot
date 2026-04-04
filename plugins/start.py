#(©)CodeXBotz

import os
import asyncio
import time
import secrets
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated, UserNotParticipant

from bot import Bot
from config import ADMINS, FORCE_MSG, START_MSG, CUSTOM_CAPTION, DISABLE_CHANNEL_BUTTON, PROTECT_CONTENT, START_PIC, AUTO_DELETE_TIME, AUTO_DELETE_MSG, JOIN_REQUEST_ENABLE, FORCE_SUB_CHANNELS, SHORTNER_API
from helper_func import subscribed, decode, get_messages, delete_file
from database.database import add_user, del_user, full_userbase, present_user, save_token, get_token

TOKEN_VALIDITY = 21600


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
    user_id = message.from_user.id

    if not await present_user(user_id):
        try:
            await add_user(user_id)
        except:
            pass

    text = message.text

    # 🔐 TOKEN CHECK
    token_valid = False
    if len(text.split()) > 1:
        token = text.split(" ", 1)[1]
        data = await get_token(token)
        if data and time.time() - data["time"] <= TOKEN_VALIDITY:
            token_valid = True

    # 🔒 FORCE SUB
    if FORCE_SUB_CHANNELS:
        joined = await is_joined(client, user_id)

        if not joined:
            buttons = []

            for ch in FORCE_SUB_CHANNELS:
                try:
                    member = await client.get_chat_member(ch, user_id)

                    # skip joined channels
                    if member.status not in ["left", "kicked"]:
                        continue

                    invite = await client.create_chat_invite_link(ch)
                    buttons.append(
                        [InlineKeyboardButton("Join Channel", url=invite.invite_link)]
                    )

                except UserNotParticipant:
                    invite = await client.create_chat_invite_link(ch)
                    buttons.append(
                        [InlineKeyboardButton("Join Channel", url=invite.invite_link)]
                    )

                except:
                    pass

            # 🔄 TRY AGAIN
            try:
                if len(text.split()) > 1:
                    buttons.append(
                        [InlineKeyboardButton("🔄 Try Again", url=f"https://t.me/{client.username}?start={text.split(' ',1)[1]}")]
                    )
                else:
                    buttons.append(
                        [InlineKeyboardButton("🔄 Try Again", url=f"https://t.me/{client.username}")]
                    )
            except:
                pass

            return await message.reply(
                FORCE_MSG.format(
                    first=message.from_user.first_name,
                    last=message.from_user.last_name,
                    username=None if not message.from_user.username else '@' + message.from_user.username,
                    mention=message.from_user.mention,
                    id=message.from_user.id
                ),
                reply_markup=InlineKeyboardMarkup(buttons),
                disable_web_page_preview=True
            )

    # 🔗 SHORTENER (FILE OPEN TIME ONLY)
    if len(text) > 7 and not token_valid:
        token = secrets.token_hex(8)
        await save_token(token, user_id)

        deep_link = f"https://t.me/{client.username}?start={token}"
        short_url = f"{SHORTNER_API}{deep_link}"

        return await message.reply(
            "🔓 Access your file here:\n" + short_url
        )

    # 📂 FILE SYSTEM (ORIGINAL SAFE)
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
            ids = range(start, end + 1) if start <= end else []

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

        for msg in messages:
            try:
                await msg.copy(chat_id=user_id, protect_content=PROTECT_CONTENT)
            except:
                pass

        return

    # 🏠 START
    else:
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
                reply_markup=reply_markup
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
                disable_web_page_preview=True
            )
