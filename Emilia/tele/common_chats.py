from telethon.tl.functions.messages import GetCommonChatsRequest
from Emilia import telethn
from Emilia.custom_filter import register
from Emilia.helper.get_user import get_user_id as tele_get_user

__mod_name__ = "Common Chats"
__help__ = """
• `/commonchats` [reply/@username/user_id] — Show groups you share with a user.
"""


@register(pattern="commonchats")
async def common_chats_cmd(event):
    reply = await event.get_reply_message()
    args = event.message.text.split(None, 1)

    user_id = None
    if reply:
        user_id = reply.sender_id
    elif len(args) > 1:
        arg = args[1].strip()
        if arg.lstrip("-").isdigit():
            user_id = int(arg)
        else:
            try:
                u = await telethn.get_entity(arg.lstrip("@"))
                user_id = u.id
            except Exception:
                return await event.reply("❌ Can't find that user.")
    else:
        return await event.reply("Reply to a user or provide @username / user_id.\n**Usage:** `/commonchats @username`")

    msg = await event.reply("🔍 Fetching common chats...")

    try:
        result = await telethn(GetCommonChatsRequest(user_id=user_id, max_id=0, limit=100))
        chats = result.chats

        if not chats:
            return await msg.edit("No common groups found with that user.")

        lines = [f"**👥 Common Groups ({len(chats)}):**\n"]
        for chat in chats:
            title = getattr(chat, "title", "Unknown")
            chat_id = chat.id
            username = getattr(chat, "username", None)
            link = f"https://t.me/{username}" if username else f"`-100{chat_id}`"
            lines.append(f"• [{title}]({link})")

        await msg.edit("\n".join(lines), link_preview=False)

    except Exception as e:
        await msg.edit(f"❌ Error: {e}")
