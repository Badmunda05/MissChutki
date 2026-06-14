import html
from pyrogram import Client
from pyrogram.errors import ChatAdminRequired, PeerIdInvalid, UserAdminInvalid
from pyrogram.types import ChatPermissions, Message

from Emilia import OWNER_ID, DEV_USERS, custom_filter
from Emilia.helper.get_user import get_user_id
from Emilia.mongo.disasters_mongo import is_dragon, is_demon

__mod_name__ = "Remote Commands"
__help__ = """
**Remote Commands** — Control other groups from anywhere (Owner/Sudo only)

• `/rban` [chat_id] [user_id/@username/reply] — Remotely ban a user from another group.
• `/runban` [chat_id] [user_id/@username] — Remotely unban.
• `/rkick` [chat_id] [user_id/@username/reply] — Remotely kick a user.
• `/rmute` [chat_id] [user_id/@username/reply] — Remotely mute a user.
• `/runmute` [chat_id] [user_id/@username] — Remotely unmute.

**Example:** `/rban -1001234567890 @username`
"""

MUTE_PERMS = ChatPermissions(can_send_messages=False)
UNMUTE_PERMS = ChatPermissions(
    can_send_messages=True,
    can_send_media_messages=True,
    can_send_polls=True,
    can_add_web_page_previews=True,
)


async def _is_elevated(client: Client, uid: int) -> bool:
    return uid == OWNER_ID or uid in DEV_USERS or await is_dragon(uid) or await is_demon(uid)


def _parse_args(message: Message):
    """Returns (chat_id_str, remaining_args)"""
    args = message.command
    if len(args) < 2:
        return None, None
    chat_id = args[1]
    rest = args[2:] if len(args) > 2 else []
    return chat_id, rest


@Client.on_message(custom_filter.command(commands=["rban"]))
async def rban_cmd(client: Client, message: Message):
    if not await _is_elevated(client, message.from_user.id):
        return await message.reply("❌ Owner/Sudo/Support only.")

    chat_id_str, rest = _parse_args(message)
    if not chat_id_str:
        return await message.reply("**Usage:** `/rban -1001234567890 @username`")

    # Get user from reply or arg
    user = await get_user_id(message, args_offset=2)
    if not user:
        return await message.reply("Can't find that user. Provide user_id or @username as 2nd arg.")

    try:
        await client.ban_chat_member(int(chat_id_str), user.id)
        name = html.escape(user.first_name or str(user.id))
        await message.reply(f"✅ Remotely banned <b>{name}</b> from <code>{chat_id_str}</code>.", parse_mode="html")
    except PeerIdInvalid:
        await message.reply("❌ Invalid chat ID or I'm not in that group.")
    except ChatAdminRequired:
        await message.reply("❌ I'm not admin in that group.")
    except Exception as e:
        await message.reply(f"❌ Error: {e}")


@Client.on_message(custom_filter.command(commands=["runban"]))
async def runban_cmd(client: Client, message: Message):
    if not await _is_elevated(client, message.from_user.id):
        return await message.reply("❌ Owner/Sudo/Support only.")

    chat_id_str, _ = _parse_args(message)
    if not chat_id_str:
        return await message.reply("**Usage:** `/runban -1001234567890 @username`")

    user = await get_user_id(message, args_offset=2)
    if not user:
        return await message.reply("Can't find that user.")

    try:
        await client.unban_chat_member(int(chat_id_str), user.id)
        name = html.escape(user.first_name or str(user.id))
        await message.reply(f"✅ Remotely unbanned <b>{name}</b> from <code>{chat_id_str}</code>.", parse_mode="html")
    except PeerIdInvalid:
        await message.reply("❌ Invalid chat ID or I'm not in that group.")
    except ChatAdminRequired:
        await message.reply("❌ I'm not admin in that group.")
    except Exception as e:
        await message.reply(f"❌ Error: {e}")


@Client.on_message(custom_filter.command(commands=["rkick"]))
async def rkick_cmd(client: Client, message: Message):
    if not await _is_elevated(client, message.from_user.id):
        return await message.reply("❌ Owner/Sudo/Support only.")

    chat_id_str, _ = _parse_args(message)
    if not chat_id_str:
        return await message.reply("**Usage:** `/rkick -1001234567890 @username`")

    user = await get_user_id(message, args_offset=2)
    if not user:
        return await message.reply("Can't find that user.")

    try:
        await client.ban_chat_member(int(chat_id_str), user.id)
        await client.unban_chat_member(int(chat_id_str), user.id)
        name = html.escape(user.first_name or str(user.id))
        await message.reply(f"✅ Remotely kicked <b>{name}</b> from <code>{chat_id_str}</code>.", parse_mode="html")
    except PeerIdInvalid:
        await message.reply("❌ Invalid chat ID or I'm not in that group.")
    except ChatAdminRequired:
        await message.reply("❌ I'm not admin in that group.")
    except Exception as e:
        await message.reply(f"❌ Error: {e}")


@Client.on_message(custom_filter.command(commands=["rmute"]))
async def rmute_cmd(client: Client, message: Message):
    if not await _is_elevated(client, message.from_user.id):
        return await message.reply("❌ Owner/Sudo/Support only.")

    chat_id_str, _ = _parse_args(message)
    if not chat_id_str:
        return await message.reply("**Usage:** `/rmute -1001234567890 @username`")

    user = await get_user_id(message, args_offset=2)
    if not user:
        return await message.reply("Can't find that user.")

    try:
        await client.restrict_chat_member(int(chat_id_str), user.id, MUTE_PERMS)
        name = html.escape(user.first_name or str(user.id))
        await message.reply(f"✅ Remotely muted <b>{name}</b> in <code>{chat_id_str}</code>.", parse_mode="html")
    except PeerIdInvalid:
        await message.reply("❌ Invalid chat ID or I'm not in that group.")
    except ChatAdminRequired:
        await message.reply("❌ I'm not admin in that group.")
    except Exception as e:
        await message.reply(f"❌ Error: {e}")


@Client.on_message(custom_filter.command(commands=["runmute"]))
async def runmute_cmd(client: Client, message: Message):
    if not await _is_elevated(client, message.from_user.id):
        return await message.reply("❌ Owner/Sudo/Support only.")

    chat_id_str, _ = _parse_args(message)
    if not chat_id_str:
        return await message.reply("**Usage:** `/runmute -1001234567890 @username`")

    user = await get_user_id(message, args_offset=2)
    if not user:
        return await message.reply("Can't find that user.")

    try:
        await client.restrict_chat_member(int(chat_id_str), user.id, UNMUTE_PERMS)
        name = html.escape(user.first_name or str(user.id))
        await message.reply(f"✅ Remotely unmuted <b>{name}</b> in <code>{chat_id_str}</code>.", parse_mode="html")
    except PeerIdInvalid:
        await message.reply("❌ Invalid chat ID or I'm not in that group.")
    except ChatAdminRequired:
        await message.reply("❌ I'm not admin in that group.")
    except Exception as e:
        await message.reply(f"❌ Error: {e}")
