from pyrogram import Client, filters
from pyrogram.errors import UserNotParticipant, ChannelInvalid
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from Emilia import BOT_ID, custom_filter
from Emilia.helper.chat_status import isUserAdmin, isBotAdmin
from Emilia.mongo.fsub_mongo import del_fsub, get_fsub, set_fsub

__mod_name__ = "Force Subscribe"
__help__ = """
**Force Subscribe** — Makes users join a channel before they can chat.

**Admin commands:**
• `/fsub` [@channel] — Enable force subscribe with a channel.
• `/fsub off` — Disable force subscribe.
• `/fsub` — Show current fsub status.
"""


@Client.on_message(custom_filter.command(commands=["fsub"]))
async def fsub_cmd(client: Client, message: Message):
    if not await isUserAdmin(message):
        return await message.reply("❌ Only admins can use this command.")

    chat_id = message.chat.id
    args = message.command

    if len(args) == 1:
        doc = await get_fsub(chat_id)
        if not doc:
            return await message.reply("Force subscribe is **disabled** in this group.")
        return await message.reply(f"Force subscribe is **enabled**.\nChannel: `@{doc['channel']}`")

    channel = args[1].lstrip("@")

    if channel.lower() in ["off", "disable", "no"]:
        await del_fsub(chat_id)
        return await message.reply("✅ Force subscribe **disabled**.")

    # Verify bot is admin in channel
    try:
        chat_member = await client.get_chat_member(f"@{channel}", BOT_ID)
    except (ChannelInvalid, Exception):
        return await message.reply(f"❌ I'm not in `@{channel}` or it doesn't exist.\nAdd me as admin first!")

    await set_fsub(chat_id, channel)
    await message.reply(f"✅ Force subscribe **enabled** for `@{channel}`.")


@Client.on_message(filters.group & ~filters.service, group=3)
async def fsub_checker(client: Client, message: Message):
    """Check if user is subscribed to the required channel."""
    if not message.from_user:
        return

    chat_id = message.chat.id
    user_id = message.from_user.id

    doc = await get_fsub(chat_id)
    if not doc:
        return

    channel = doc["channel"]
    try:
        await client.get_chat_member(f"@{channel}", user_id)
    except UserNotParticipant:
        try:
            await message.delete()
        except Exception:
            pass
        await message.reply(
            f"⚠️ {message.from_user.mention}, you must join our channel first!\n"
            f"Join here: https://t.me/{channel}\n\n"
            "After joining, you can chat again.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ Join Channel", url=f"https://t.me/{channel}")]
            ])
        )
    except Exception:
        pass
