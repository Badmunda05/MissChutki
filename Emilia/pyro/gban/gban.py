import html
from io import BytesIO

from pyrogram import Client, filters
from pyrogram.errors import PeerIdInvalid, UserIsBlocked
from pyrogram.types import Message

from Emilia import BOT_ID, DEV_USERS, OWNER_ID, custom_filter, db
from Emilia.helper.chat_status import isBotAdmin, isUserAdmin
from Emilia.helper.get_user import get_user_id
from Emilia.mongo.gban_mongo import (
    add_gban,
    get_gban,
    get_gban_list,
    gban_count,
    is_gbanned,
    remove_gban,
)
from Emilia.mongo.users_mongo import chats

__mod_name__ = "GBan"
__help__ = """
**Global Ban** — Owner/Dev only

• `/gban` [reply | user_id | @username] [reason] — Globally ban a user from all groups.
• `/ungban` [reply | user_id | @username] — Remove a user from global ban.
• `/gbanlist` — List all globally banned users.
• `/gbancount` — Show total number of gbanned users.
"""


def _is_dev(user_id: int) -> bool:
    return user_id in DEV_USERS or user_id == OWNER_ID


@Client.on_message(custom_filter.command(commands=["gban", "globalban"]))
async def gban_user(client: Client, message: Message):
    if not _is_dev(message.from_user.id):
        return await message.reply("❌ This command is for **Owners/Devs** only.")

    user_info = await get_user_id(message)
    if not user_info:
        return await message.reply("I can't find that user.")

    user_id = user_info.id
    reason = " ".join(message.command[1:]) if not message.reply_to_message else " ".join(message.command[1:])

    if message.reply_to_message:
        reason = " ".join(message.command[1:])
    else:
        reason = " ".join(message.command[2:]) if len(message.command) > 2 else ""

    if user_id == BOT_ID:
        return await message.reply("I can't gban myself!")

    if user_id in DEV_USERS or user_id == OWNER_ID:
        return await message.reply("❌ Can't gban a dev/owner!")

    if await is_gbanned(user_id):
        return await message.reply(f"User `{user_id}` is already gbanned.")

    await add_gban(user_id, reason=reason, banned_by=message.from_user.id)

    mention = html.escape(user_info.first_name) if user_info.first_name else str(user_id)
    reason_text = f"\n**Reason:** {reason}" if reason else ""
    await message.reply(
        f"✅ **GBanned** {mention} (`{user_id}`).{reason_text}\n"
        "They will be auto-banned in all groups where I'm admin."
    )

    # Try to notify user
    try:
        await client.send_message(
            user_id,
            f"You have been **globally banned** by the bot owner.\n"
            f"{'**Reason:** ' + reason if reason else ''}\n"
            "To appeal, contact @SpiralTechDivision",
        )
    except (UserIsBlocked, PeerIdInvalid):
        pass

    # Ban from current chat immediately
    try:
        await client.ban_chat_member(message.chat.id, user_id)
    except Exception:
        pass


@Client.on_message(custom_filter.command(commands=["ungban", "unglobalban"]))
async def ungban_user(client: Client, message: Message):
    if not _is_dev(message.from_user.id):
        return await message.reply("❌ This command is for **Owners/Devs** only.")

    user_info = await get_user_id(message)
    if not user_info:
        return await message.reply("I can't find that user.")

    user_id = user_info.id

    if not await is_gbanned(user_id):
        return await message.reply(f"User `{user_id}` is not gbanned.")

    await remove_gban(user_id)
    mention = html.escape(user_info.first_name) if user_info.first_name else str(user_id)
    await message.reply(f"✅ **UnGbanned** {mention} (`{user_id}`).")

    try:
        await client.send_message(
            user_id,
            "You have been **removed** from the global ban list. Welcome back!",
        )
    except (UserIsBlocked, PeerIdInvalid):
        pass


@Client.on_message(custom_filter.command(commands=["gbanlist", "globalbanlist"]))
async def gban_list(client: Client, message: Message):
    if not _is_dev(message.from_user.id):
        return await message.reply("❌ This command is for **Owners/Devs** only.")

    banned = await get_gban_list()
    if not banned:
        return await message.reply("No users are globally banned.")

    text = "**🚫 Globally Banned Users:**\n\n"
    for doc in banned:
        uid = doc["user_id"]
        rsn = doc.get("reason") or "No reason"
        text += f"• `{uid}` — {rsn}\n"

    if len(text) > 4096:
        with BytesIO(text.encode()) as f:
            f.name = "gbanlist.txt"
            await message.reply_document(f, caption="Global ban list (too long for message)")
    else:
        await message.reply(text)


@Client.on_message(custom_filter.command(commands=["gbancount"]))
async def gban_count_cmd(_, message: Message):
    if not _is_dev(message.from_user.id):
        return await message.reply("❌ This command is for **Owners/Devs** only.")
    count = await gban_count()
    await message.reply(f"**Total GBanned Users:** `{count}`")
