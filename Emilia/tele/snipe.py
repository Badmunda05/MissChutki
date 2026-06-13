from telethon import events

from Emilia import telethn
from Emilia.custom_filter import register

__mod_name__ = "Snipe"
__help__ = """
• `/snipe` — Show the last deleted message in the chat.
"""

_snipe_cache = {}


@telethn.on(events.MessageDeleted)
async def catch_deleted(event):
    chat_id = event.chat_id
    if not chat_id:
        return
    msg_ids = event.deleted_ids
    if msg_ids:
        _snipe_cache[chat_id] = msg_ids[-1]


@register(pattern="snipe")
async def snipe_cmd(event):
    chat_id = event.chat_id
    if chat_id not in _snipe_cache:
        return await event.reply("No deleted messages cached yet in this chat.")

    msg_id = _snipe_cache[chat_id]
    await event.reply(f"🔍 Last deleted message ID: `{msg_id}`\n_(Content cannot be retrieved after deletion)_")
