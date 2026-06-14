import asyncio, random
from pyrogram import Client
from pyrogram.errors import FloodWait
from pyrogram.types import Message
from Emilia import custom_filter
from Emilia.helper.chat_status import isUserAdmin

__mod_name__ = "VC Tag"
__help__ = """
• `/hitag` [message] — Tag all group members with a fun message to join VC.
• `/ntag` [message] — Tag everyone in the group.
• `/histop` or `/nstop` — Stop ongoing tag.
"""

_spam = {}
EMOJIS = ["🌸","💫","🎵","🔊","✨","🌺","💐","🎤","🎙","🌟","🦋","🎶"]
LINES = [
    "🎙 **VC chal raha hai! Aa jao!**",
    "🔊 **Come join the Voice Chat now!**",
    "📢 **Everyone is waiting for you in VC!**",
    "🌸 **VC mein aa jao yaar~**",
    "💫 **Sab log VC mein hain, tu kab aa raha?**",
]


@Client.on_message(custom_filter.command(commands=["hitag"]))
async def hitag_cmd(client: Client, message: Message):
    if not await isUserAdmin(message):
        return await message.reply("❌ Admins only.")
    chat_id = message.chat.id
    _spam[chat_id] = True
    custom_msg = " ".join(message.command[1:]) if len(message.command) > 1 else random.choice(LINES)

    try:
        members = [m.user async for m in client.get_chat_members(chat_id) if not m.user.is_bot and not m.user.is_deleted]
    except Exception as e:
        return await message.reply(f"❌ {e}")

    await message.reply(f"📢 Tagging **{len(members)}** members... `/histop` to cancel.")

    for i in range(0, len(members), 5):
        if not _spam.get(chat_id):
            return await message.reply("⏹ Stopped.")
        chunk = members[i:i+5]
        text = f"{random.choice(EMOJIS)} {custom_msg}\n\n" + " ".join(f"[{u.first_name}](tg://user?id={u.id})" for u in chunk)
        try:
            await client.send_message(chat_id, text)
        except FloodWait as fw:
            await asyncio.sleep(fw.value + 1)
        except Exception:
            pass
        await asyncio.sleep(1.5)

    _spam.pop(chat_id, None)
    await message.reply("✅ All members tagged!")


@Client.on_message(custom_filter.command(commands=["histop", "nstop"]))
async def stop_tag(_, message: Message):
    if not await isUserAdmin(message):
        return await message.reply("❌ Admins only.")
    _spam[message.chat.id] = False
    await message.reply("⏹ Tag stopped.")
