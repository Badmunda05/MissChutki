from pyrogram import Client, filters
from pyrogram.errors import ChatAdminRequired, UserAdminInvalid
from pyrogram.types import Message

from Emilia import LOGGER
from Emilia.mongo.gban_mongo import is_gbanned, get_gban
from Emilia.mongo.disasters_mongo import is_wolf

__mod_name__ = "GBan Watcher"


@Client.on_message(filters.group, group=5)
async def gban_watcher(client: Client, message: Message):
    if not message.from_user:
        return
    user_id = message.from_user.id

    try:
        # Wolves are immune to gban
        if await is_wolf(user_id):
            return

        if not await is_gbanned(user_id):
            return

        doc = await get_gban(user_id)
        reason = doc.get("reason") or "No reason provided"

        try:
            await client.ban_chat_member(message.chat.id, user_id)
            try:
                await message.delete()
            except Exception:
                pass
            await message.reply(
                f"⚠️ <b>GBanned user detected!</b>\n"
                f"<b>User:</b> <a href='tg://user?id={user_id}'>{message.from_user.first_name}</a> (<code>{user_id}</code>)\n"
                f"<b>Reason:</b> {reason}",
                parse_mode="html",
            )
        except (ChatAdminRequired, UserAdminInvalid):
            pass

    except Exception as e:
        LOGGER.error(f"GBan watcher error: {e}")
