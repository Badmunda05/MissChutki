from pyrogram import Client, filters
from pyrogram.errors import ChatAdminRequired, UserAdminInvalid
from pyrogram.types import ChatPermissions, Message

from Emilia import LOGGER
from Emilia.mongo.gban_mongo import is_gmuted, get_gmute
from Emilia.mongo.disasters_mongo import is_wolf

__mod_name__ = "GMute Watcher"

MUTE_PERMS = ChatPermissions(
    can_send_messages=False,
    can_send_media_messages=False,
    can_send_polls=False,
    can_add_web_page_previews=False,
)


@Client.on_message(filters.group, group=6)
async def gmute_watcher(client: Client, message: Message):
    if not message.from_user:
        return
    user_id = message.from_user.id

    try:
        if await is_wolf(user_id):
            return

        if not await is_gmuted(user_id):
            return

        doc = await get_gmute(user_id)
        reason = doc.get("reason") or "No reason provided"

        try:
            await client.restrict_chat_member(message.chat.id, user_id, MUTE_PERMS)
            try:
                await message.delete()
            except Exception:
                pass
            await message.reply(
                f"🔇 <b>GMuted user detected!</b>\n"
                f"<b>User:</b> <a href='tg://user?id={user_id}'>{message.from_user.first_name}</a> (<code>{user_id}</code>)\n"
                f"<b>Reason:</b> {reason}",
                parse_mode="html",
            )
        except (ChatAdminRequired, UserAdminInvalid):
            pass

    except Exception as e:
        LOGGER.error(f"GMute watcher error: {e}")
