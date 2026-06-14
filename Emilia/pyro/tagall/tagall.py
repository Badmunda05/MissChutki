import asyncio
from pyrogram import Client
from pyrogram.errors import FloodWait
from pyrogram.types import Message

from Emilia import custom_filter
from Emilia.helper.chat_status import isUserAdmin

__mod_name__ = "Tag All"
__help__ = """
• `/tagall` [message] — Mention all members in the group (admin only).
• `/canceltagall` — Cancel an ongoing tagall.
"""

_cancel_flag = {}


@Client.on_message(custom_filter.command(commands=["tagall"]))
async def tagall_cmd(client: Client, message: Message):
    if not await isUserAdmin(message):
        return await message.reply("❌ Only admins can use this.")

    chat_id = message.chat.id
    _cancel_flag[chat_id] = False

    custom_msg = " ".join(message.command[1:]) if len(message.command) > 1 else ""
    header = f"📢 **Tagging all members!**{' — ' + custom_msg if custom_msg else ''}\n\n"

    try:
        members = []
        async for member in client.get_chat_members(chat_id):
            if not member.user.is_bot and not member.user.is_deleted:
                members.append(member.user)
    except Exception as e:
        return await message.reply(f"❌ Could not get members: {e}")

    batch_size = 5
    for i in range(0, len(members), batch_size):
        if _cancel_flag.get(chat_id):
            await message.reply("❌ TagAll cancelled.")
            break

        batch = members[i:i + batch_size]
        text = header + " ".join(f"[{m.first_name}](tg://user?id={m.id})" for m in batch)

        try:
            await client.send_message(chat_id, text)
        except FloodWait as fw:
            await asyncio.sleep(fw.value)
        except Exception:
            pass
        await asyncio.sleep(1)
    else:
        await message.reply("✅ All members tagged!")


@Client.on_message(custom_filter.command(commands=["canceltagall"]))
async def cancel_tagall(_, message: Message):
    chat_id = message.chat.id
    if not await isUserAdmin(message):
        return await message.reply("❌ Only admins can cancel.")
    _cancel_flag[chat_id] = True
    await message.reply("⏹ Cancelling tagall...")
