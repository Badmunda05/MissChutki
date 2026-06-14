import html
from io import BytesIO

from pyrogram import Client
from pyrogram.errors import PeerIdInvalid, UserIsBlocked
from pyrogram.types import ChatPermissions, Message

from Emilia import BOT_ID, DEV_USERS, OWNER_ID, custom_filter
from Emilia.helper.get_user import get_user_id
from Emilia.mongo.gban_mongo import (
    add_gmute,
    get_gmute,
    get_gmute_list,
    gmute_count,
    is_gmuted,
    remove_gmute,
)

__mod_name__ = "GMute"
__help__ = """
**Global Mute** — Owner/Dev only

• `/gmute` [reply | user_id | @username] [reason] — Globally mute a user in all groups.
• `/ungmute` [reply | user_id | @username] — Remove global mute from a user.
• `/gmutelist` — List all globally muted users.
• `/gmutecount` — Show total gmuted users.
"""

MUTE_PERMS = ChatPermissions(
    can_send_messages=False,
    can_send_media_messages=False,
    can_send_polls=False,
    can_add_web_page_previews=False,
    can_change_info=False,
    can_invite_users=False,
    can_pin_messages=False,
)


def _is_dev(user_id: int) -> bool:
    return user_id in DEV_USERS or user_id == OWNER_ID


@Client.on_message(custom_filter.command(commands=["gmute", "globalmute"]))
async def gmute_user(client: Client, message: Message):
    if not _is_dev(message.from_user.id):
        return await message.reply("❌ This command is for **Owners/Devs** only.")

    user_info = await get_user_id(message)
    if not user_info:
        return await message.reply("I can't find that user.")

    user_id = user_info.id

    if message.reply_to_message:
        reason = " ".join(message.command[1:])
    else:
        reason = " ".join(message.command[2:]) if len(message.command) > 2 else ""

    if user_id == BOT_ID:
        return await message.reply("I can't gmute myself!")

    if user_id in DEV_USERS or user_id == OWNER_ID:
        return await message.reply("❌ Can't gmute a dev/owner!")

    if await is_gmuted(user_id):
        return await message.reply(f"User `{user_id}` is already gmuted.")

    await add_gmute(user_id, reason=reason, muted_by=message.from_user.id)

    mention = html.escape(user_info.first_name) if user_info.first_name else str(user_id)
    reason_text = f"\n**Reason:** {reason}" if reason else ""
    await message.reply(
        f"🔇 **GMuted** {mention} (`{user_id}`).{reason_text}\n"
        "They will be auto-muted in all groups where I'm admin."
    )

    try:
        await client.restrict_chat_member(message.chat.id, user_id, MUTE_PERMS)
    except Exception:
        pass

    try:
        await client.send_message(
            user_id,
            f"You have been **globally muted** by the bot owner.\n"
            f"{'**Reason:** ' + reason if reason else ''}",
        )
    except (UserIsBlocked, PeerIdInvalid):
        pass


@Client.on_message(custom_filter.command(commands=["ungmute", "unglobalmute"]))
async def ungmute_user(client: Client, message: Message):
    if not _is_dev(message.from_user.id):
        return await message.reply("❌ This command is for **Owners/Devs** only.")

    user_info = await get_user_id(message)
    if not user_info:
        return await message.reply("I can't find that user.")

    user_id = user_info.id

    if not await is_gmuted(user_id):
        return await message.reply(f"User `{user_id}` is not gmuted.")

    await remove_gmute(user_id)
    mention = html.escape(user_info.first_name) if user_info.first_name else str(user_id)
    await message.reply(f"🔊 **UnGmuted** {mention} (`{user_id}`).")

    try:
        await client.send_message(user_id, "You have been **removed** from the global mute list.")
    except (UserIsBlocked, PeerIdInvalid):
        pass


@Client.on_message(custom_filter.command(commands=["gmutelist"]))
async def gmute_list_cmd(_, message: Message):
    if not _is_dev(message.from_user.id):
        return await message.reply("❌ This command is for **Owners/Devs** only.")

    muted = await get_gmute_list()
    if not muted:
        return await message.reply("No users are globally muted.")

    text = "**🔇 Globally Muted Users:**\n\n"
    for doc in muted:
        uid = doc["user_id"]
        rsn = doc.get("reason") or "No reason"
        text += f"• `{uid}` — {rsn}\n"

    if len(text) > 4096:
        with BytesIO(text.encode()) as f:
            f.name = "gmutelist.txt"
            await message.reply_document(f, caption="Global mute list")
    else:
        await message.reply(text)


@Client.on_message(custom_filter.command(commands=["gmutecount"]))
async def gmute_count_cmd(_, message: Message):
    if not _is_dev(message.from_user.id):
        return await message.reply("❌ This command is for **Owners/Devs** only.")
    count = await gmute_count()
    await message.reply(f"**Total GMuted Users:** `{count}`")
