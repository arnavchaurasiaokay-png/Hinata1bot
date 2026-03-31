#(©)CodeXBotz

import asyncio
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait, UserNotParticipant

from bot import Bot
from config import ADMINS, FORCE_MSG, START_MSG, CUSTOM_CAPTION, PROTECT_CONTENT, START_PIC, AUTO_DELETE_TIME, AUTO_DELETE_MSG, FORCE_SUB_CHANNEL
from helper_func import decode, get_messages
from database.database import add_user, full_userbase, present_user


# 🔥 FORCE SUB FUNCTION (FINAL FIX)
async def is_subscribed(client, user_id):
    try:
        await client.get_chat_member(FORCE_SUB_CHANNEL, user_id)
        return True
    except UserNotParticipant:
        return False
    except Exception:
        return True


# 🔥 START COMMAND
@Bot.on_message(filters.command('start') & filters.private)
async def start_command(client: Client, message: Message):

    user_id = message.from_user.id

    # 🔒 FORCE SUB CHECK (FIXED)
    if FORCE_SUB_CHANNEL:
        if not await is_subscribed(client, user_id):

            buttons = [
                [InlineKeyboardButton("📢 Join Channel", url=f"https://t.me/{FORCE_SUB_CHANNEL}")],
                [InlineKeyboardButton("✅ Verify", callback_data="checksub")]
            ]

            await message.reply(
                text="🚫 Please join our channel first then click VERIFY",
                reply_markup=InlineKeyboardMarkup(buttons),
                quote=True
            )
            return


    # ✅ USER SAVE
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

        # 🔥 MAIN FIX (NO BUTTON COPY)
        for msg in messages:
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

                caption = msg.caption.html if msg.caption else ""

                if file_id:
                    await client.send_cached_media(
                        chat_id=user_id,
                        file_id=file_id,
                        caption=caption,
                        parse_mode=ParseMode.HTML,
                        protect_content=PROTECT_CONTENT
                    )

            except FloodWait as e:
                await asyncio.sleep(e.value)
            except Exception:
                continue

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


# 🔥 VERIFY BUTTON (FIXED)
@Bot.on_callback_query(filters.regex("checksub"))
async def verify_sub(client, query):

    user_id = query.from_user.id

    if FORCE_SUB_CHANNEL:
        if not await is_subscribed(client, user_id):
            await query.answer("❌ Join channel first", show_alert=True)
            return

    await query.message.edit("✅ Verified! Now send /start again")
    await query.answer()


# 👥 USERS
@Bot.on_message(filters.command('users') & filters.private & filters.user(ADMINS))
async def get_users(client: Bot, message: Message):
    users = await full_userbase()
    await message.reply(f"{len(users)} users are using this bot")
