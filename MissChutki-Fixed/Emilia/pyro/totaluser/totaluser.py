import os
from pyrogram import Client
from pyrogram.types import Message
from Emilia import custom_filter
from Emilia.helper.chat_status import isUserAdmin

__mod_name__ = "User List"
__help__ = """
• `/user` — Export all group members & bots as .txt files.
"""


@Client.on_message(custom_filter.command(commands=["user", "memberlist", "users"]))
async def get_users_cmd(client: Client, message: Message):
    if message.chat.type.value == "private":
        return await message.reply("Groups mein use karo.")
    if not await isUserAdmin(message):
        return await message.reply("❌ Admins only.")

    msg = await message.reply("📊 Scanning members...")
    members_list, bot_list, count = [], [], 0

    try:
        async for member in client.get_chat_members(message.chat.id):
            u = member.user
            if u.is_bot:
                bot_list.append(f"@{u.username}" if u.username else f"NoUsername (ID: {u.id})")
            else:
                count += 1
                members_list.append(f"{count}. {u.first_name or 'NoName'} | @{u.username or 'NoUsername'} | {u.id}")
    except Exception as e:
        return await msg.edit(f"❌ {e}")

    with open("Members.txt", "w", encoding="utf-8") as f:
        f.write(f"Group: {message.chat.title}\nTotal Users: {count}\n\n" + "\n".join(members_list))
    with open("Bots.txt", "w", encoding="utf-8") as f:
        f.write(f"Group: {message.chat.title}\nTotal Bots: {len(bot_list)}\n\n" + "\n".join(bot_list))

    await msg.delete()
    await message.reply_document("Members.txt", caption=f"👥 **{count} members** in {message.chat.title}")
    await message.reply_document("Bots.txt", caption=f"🤖 **{len(bot_list)} bots** in {message.chat.title}")
    os.remove("Members.txt")
    os.remove("Bots.txt")
