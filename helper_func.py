#(©)Codexbotz

import base64
import re
import asyncio
from pyrogram import filters
from pyrogram.enums import ChatMemberStatus
from config import FORCE_SUB_CHANNELS, ADMINS, AUTO_DELETE_TIME, AUTO_DEL_SUCCESS_MSG
from pyrogram.errors import FloodWait
from pyrogram.errors.exceptions.bad_request_400 import UserNotParticipant


# 🔒 FORCE SUB CHECK (FINAL FIX)
async def is_subscribed(filter, client, message):

    # अगर कोई channel set नहीं है → allow
    if not FORCE_SUB_CHANNELS:
        return True

    # safety check
    user = message.from_user
    if not user:
        return False

    user_id = user.id

    # admin bypass
    if user_id in ADMINS:
        return True

    # 🔥 check all channels strictly
    for ch in FORCE_SUB_CHANNELS:
        try:
            member = await client.get_chat_member(ch, user_id)

            # ❌ अगर user joined नहीं है
            if member.status in [
                ChatMemberStatus.LEFT,
                ChatMemberStatus.BANNED
            ]:
                return False

        except UserNotParticipant:
            return False

        except Exception as e:
            print(f"ForceSub Error: {e}")
            return False

    return True


# 🔐 ENCODE
async def encode(string):
    string_bytes = string.encode("ascii")
    base64_bytes = base64.urlsafe_b64encode(string_bytes)
    return base64_bytes.decode("ascii").strip("=")


# 🔓 DECODE
async def decode(base64_string):
    base64_string = base64_string.strip("=")
    base64_bytes = (base64_string + "=" * (-len(base64_string) % 4)).encode("ascii")
    string_bytes = base64.urlsafe_b64decode(base64_bytes)
    return string_bytes.decode("ascii")


# 📩 GET MESSAGES
async def get_messages(client, message_ids):
    messages = []
    total_messages = 0

    while total_messages != len(message_ids):
        temb_ids = message_ids[total_messages:total_messages+200]

        try:
            msgs = await client.get_messages(
                chat_id=client.db_channel.id,
                message_ids=temb_ids
            )

        except FloodWait as e:
            await asyncio.sleep(e.value)
            msgs = await client.get_messages(
                chat_id=client.db_channel.id,
                message_ids=temb_ids
            )

        except:
            msgs = []

        total_messages += len(temb_ids)
        messages.extend(msgs)

    return messages


# 🔍 GET MESSAGE ID FROM LINK
async def get_message_id(client, message):

    if message.forward_from_chat:
        if message.forward_from_chat.id == client.db_channel.id:
            return message.forward_from_message_id
        return 0

    elif message.forward_sender_name:
        return 0

    elif message.text:
        pattern = "https://t.me/(?:c/)?(.*)/(\\d+)"
        matches = re.match(pattern, message.text)

        if not matches:
            return 0

        channel_id = matches.group(1)
        msg_id = int(matches.group(2))

        if channel_id.isdigit():
            if f"-100{channel_id}" == str(client.db_channel.id):
                return msg_id
        else:
            if channel_id == client.db_channel.username:
                return msg_id

    return 0


# ⏱ UPTIME FORMAT
def get_readable_time(seconds: int) -> str:
    count = 0
    up_time = ""
    time_list = []
    time_suffix_list = ["s", "m", "h", "days"]

    while count < 4:
        count += 1
        remainder, result = divmod(seconds, 60) if count < 3 else divmod(seconds, 24)

        if seconds == 0 and remainder == 0:
            break

        time_list.append(int(result))
        seconds = int(remainder)

    time_list = [str(time_list[i]) + time_suffix_list[i] for i in range(len(time_list))]

    if len(time_list) == 4:
        up_time += f"{time_list.pop()}, "

    time_list.reverse()
    up_time += ":".join(time_list)

    return up_time


# 🗑 AUTO DELETE FILE
async def delete_file(messages, client, process):
    await asyncio.sleep(AUTO_DELETE_TIME)

    for msg in messages:
        try:
            await client.delete_messages(chat_id=msg.chat.id, message_ids=[msg.id])
        except Exception as e:
            try:
                await asyncio.sleep(e.x)
            except:
                pass
            print(f"Failed to delete {msg.id}: {e}")

    await process.edit_text(AUTO_DEL_SUCCESS_MSG)


# 🔗 FILTER
subscribed = filters.create(is_subscribed)
