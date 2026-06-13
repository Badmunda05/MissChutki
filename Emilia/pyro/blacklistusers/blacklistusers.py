import html
from pyrogram import Client, filters
from pyrogram.types import Message

from Emilia import OWNER_ID, DEV_USERS, custom_filter
from Emilia.helper.get_user import get_user_id
from Emilia.mongo.blacklistusers_mongo import (
    add_bluser, remove_bluser, is_bluser, get_bluserlist
)

__mod_name__ = "Blacklist Users"
__help__ = """
**Blacklist Users** — Bot ignores these users completely (owner/sudo only)

• `/bluser` [reply/id/@username] [reason] — Bot will ignore this user.
• `/unbluser` [reply/id/@username] — Remove from ignore list.
• `/bllist` — Show all ignored users.

ℹ️ Different from /gban — user is NOT banned, bot just won't respond to them.
"""


def _is_elevated(uid):
    return uid == OWNER_ID or uid in DEV_USERS


@Client.on_message(custom_filter.command(commands=["bluser", "blacklistuser"]))
async def bluser_cmd(client: Client, message: Message):
    if not _is_elevated(message.from_user.id):
        return await message.reply("❌ Owner/Sudo only.")
    user = await get_user_id(message)
    if not user:
        return await message.reply("Can't find that user.")
    if user.id == OWNER_ID or user.id in DEV_USERS:
        return await message.reply("❌ Can't blacklist an elevated user!")
    reason = " ".join(message.command[1:]) if not message.reply_to_message else " ".join(message.command[1:])
    if message.reply_to_message:
        reason = " ".join(message.command[1:])
    else:
        reason = " ".join(message.command[2:]) if len(message.command) > 2 else ""

    if await is_bluser(user.id):
        return await message.reply("Already in bot blacklist.")
    await add_bluser(user.id, reason)
    name = html.escape(user.first_name or str(user.id))
    await message.reply(
        f"🚫 <b>{name}</b> (<code>{user.id}</code>) added to bot blacklist.\n"
        f"{'<b>Reason:</b> ' + reason if reason else ''}",
        parse_mode="html"
    )


@Client.on_message(custom_filter.command(commands=["unbluser", "unblacklistuser"]))
async def unbluser_cmd(client: Client, message: Message):
    if not _is_elevated(message.from_user.id):
        return await message.reply("❌ Owner/Sudo only.")
    user = await get_user_id(message)
    if not user:
        return await message.reply("Can't find that user.")
    if not await is_bluser(user.id):
        return await message.reply("This user is not in the bot blacklist.")
    await remove_bluser(user.id)
    name = html.escape(user.first_name or str(user.id))
    await message.reply(f"✅ <b>{name}</b> removed from bot blacklist.", parse_mode="html")


@Client.on_message(custom_filter.command(commands=["bllist", "blacklistlist"]))
async def bllist_cmd(client: Client, message: Message):
    if not _is_elevated(message.from_user.id):
        return await message.reply("❌ Owner/Sudo only.")
    users = await get_bluserlist()
    if not users:
        return await message.reply("No users in bot blacklist.")
    lines = ["**🚫 Bot Blacklisted Users:**\n"]
    for doc in users:
        uid = doc["uid"]
        rsn = doc.get("reason") or "No reason"
        lines.append(f"• <code>{uid}</code> — {rsn}")
    await message.reply("\n".join(lines), parse_mode="html")


# ─── WATCHER: silently ignore bluser messages ───────────────────
@Client.on_message(filters.group | filters.private, group=2)
async def bluser_watcher(_, message: Message):
    if not message.from_user:
        return
    if await is_bluser(message.from_user.id):
        message.stop_propagation()
