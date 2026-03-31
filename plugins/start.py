#(©)CodeXBotz

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
    id = message.from_user.id

    if not await present_user(id):
        try:
            await add_user(id)
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
            ids = range(start, end+1) if start <= end else list(range(start, end-1, -1))

        elif len(argument) == 2:
            ids = [int(int(argument[1]) / abs(client.db_channel.id))]

        temp_msg = await message.reply("Please wait...")

        try:
            messages = await get_messages(client, ids)
        except:
            await message.reply_text("Something went wrong..!")
            return

        await temp_msg.delete()

        track_msgs = []

        for msg in messages:

            # 📄 Caption
            if CUSTOM_CAPTION and msg.document:
                caption = CUSTOM_CAPTION.format(
                    previouscaption="" if not msg.caption else msg.caption.html,
                    filename=msg.document.file_name
                )
            else:
                caption = "" if not msg.caption else msg.caption.html

            # ❌ Remove channel buttons
            reply_markup = None

            # ⏳ Auto delete system
            try:
                copied = await msg.copy(
                    chat_id=message.from_user.id,
                    caption=caption,
                    parse_mode=ParseMode.HTML,
                    reply_markup=reply_markup,
                    protect_content=PROTECT_CONTENT
                )

                if AUTO_DELETE_TIME and AUTO_DELETE_TIME > 0:
                    track_msgs.append(copied)

            except FloodWait as e:
                await asyncio.sleep(e.value)
                copied = await msg.copy(
                    chat_id=message.from_user.id,
                    caption=caption,
                    parse_mode=ParseMode.HTML,
                    reply_markup=reply_markup,
                    protect_content=PROTECT_CONTENT
                )
                if AUTO_DELETE_TIME:
                    track_msgs.append(copied)

        # 🗑 Auto delete message
        if track_msgs:
            delete_data = await client.send_message(
                chat_id=message.from_user.id,
                text=AUTO_DELETE_MSG.format(time=AUTO_DELETE_TIME)
            )
            asyncio.create_task(delete_file(track_msgs, client, delete_data))

        return

    # 🏠 NORMAL START MESSAGE
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
            reply_markup=reply_markup
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
            reply_markup=reply_markup
        )


# 🔒 FORCE SUB (MULTIPLE CHANNELS)
@Bot.on_message(filters.command('start') & filters.private)
async def not_joined(client: Client, message: Message):

    buttons = []

    # ✅ Multiple join buttons
    for i, link in enumerate(client.invitelinks):
        buttons.append(
            [InlineKeyboardButton(f"📢 Join Channel {i+1}", url=link)]
        )

    try:
        buttons.append(
            [InlineKeyboardButton(
                "🔄 Try Again",
                url=f"https://t.me/{client.username}?start={message.command[1]}"
            )]
        )
    except:
        pass

    await message.reply(
        text=FORCE_MSG.format(
            first=message.from_user.first_name,
            last=message.from_user.last_name,
            username='@' + message.from_user.username if message.from_user.username else None,
            mention=message.from_user.mention,
            id=message.from_user.id
        ),
        reply_markup=InlineKeyboardMarkup(buttons),
        disable_web_page_preview=True
    )


# 👥 USERS
@Bot.on_message(filters.command('users') & filters.private & filters.user(ADMINS))
async def get_users(client: Bot, message: Message):
    users = await full_userbase()
    await message.reply(f"{len(users)} users are using this bot")


# 📢 BROADCAST
@Bot.on_message(filters.private & filters.command('broadcast') & filters.user(ADMINS))
async def send_text(client: Bot, message: Message):

    if not message.reply_to_message:
        return await message.reply("Reply to a message to broadcast")

    users = await full_userbase()
    msg = message.reply_to_message

    success = 0

    for user in users:
        try:
            await msg.copy(user)
            success += 1
        except:
            pass

    await message.reply(f"Broadcast done to {success} users")
