from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from Emilia import EVENT_LOGS

__mod_name__ = "Group Logger"
__hidden__ = True


@Client.on_message(filters.new_chat_members)
async def bot_added(client: Client, message: Message):
    if not EVENT_LOGS:
        return
    me = await client.get_me()
    if not any(m.id == me.id for m in message.new_chat_members):
        return
    chat = message.chat
    try:
        count = await client.get_chat_members_count(chat.id)
    except Exception:
        count = "N/A"
    username = f"@{chat.username}" if chat.username else "Private"
    added_by = (f'<a href="tg://user?id={message.from_user.id}">{message.from_user.first_name}</a>'
                if message.from_user else "Unknown")
    try:
        await client.send_message(EVENT_LOGS,
            f"🎉 <b>#BotAdded</b>\n\n"
            f"• <b>Group:</b> <code>{chat.title}</code>\n"
            f"• <b>ID:</b> <code>{chat.id}</code>\n"
            f"• <b>Username:</b> {username}\n"
            f"• <b>Members:</b> <code>{count}</code>\n"
            f"• <b>Added by:</b> {added_by}",
            parse_mode="html",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("👤 Added By", url=f"tg://user?id={message.from_user.id}")
            ]]) if message.from_user else None
        )
    except Exception:
        pass


@Client.on_message(filters.left_chat_member)
async def bot_removed(client: Client, message: Message):
    if not EVENT_LOGS:
        return
    me = await client.get_me()
    if not message.left_chat_member or message.left_chat_member.id != me.id:
        return
    chat = message.chat
    removed_by = (f'<a href="tg://user?id={message.from_user.id}">{message.from_user.first_name}</a>'
                  if message.from_user else "Unknown")
    username = f"@{chat.username}" if chat.username else "Private"
    try:
        await client.send_message(EVENT_LOGS,
            f"❌ <b>#BotRemoved</b>\n\n"
            f"• <b>Group:</b> <code>{chat.title}</code>\n"
            f"• <b>ID:</b> <code>{chat.id}</code>\n"
            f"• <b>Username:</b> {username}\n"
            f"• <b>Removed by:</b> {removed_by}",
            parse_mode="html"
        )
    except Exception:
        pass
