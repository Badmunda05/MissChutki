import aiohttp
from pyrogram import Client, filters
from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import ChatAdminRequired, UserAdminInvalid
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from Emilia import EVENT_LOGS, OWNER_ID, DEV_USERS, custom_filter
from Emilia.helper.chat_status import isUserAdmin
from Emilia.helper.get_user import get_user_id
from Emilia.mongo.disasters_mongo import is_dragon

__mod_name__ = "DBan & SBan"
__help__ = """
• `/dban` [reply/@user/id] — Delete the replied message **and** ban the user. Shows unban button.
• `/sban` [reply/@user/id] — Silent ban — deletes command + replied msg silently, no notification.
"""


async def _gif():
    try:
        async with aiohttp.ClientSession() as s:
            async with s.get("https://api.waifu.pics/sfw/kick", timeout=aiohttp.ClientTimeout(total=5)) as r:
                return (await r.json()).get("url")
    except Exception:
        return None


async def _elevated(uid):
    return uid == OWNER_ID or uid in DEV_USERS or await is_dragon(uid)


@Client.on_message(custom_filter.command(commands=["dban"]))
async def dban_cmd(client: Client, message: Message):
    if not await isUserAdmin(message) and not await _elevated(message.from_user.id):
        return await message.reply("❌ Admins only.")

    user = await get_user_id(message)
    if not user:
        return await message.reply("Can't find that user.")

    uid = user.id
    if message.reply_to_message:
        try:
            await message.reply_to_message.delete()
        except Exception:
            pass

    try:
        m = await client.get_chat_member(message.chat.id, uid)
        if m.status == ChatMemberStatus.BANNED:
            return await message.reply("User is already banned.")
    except Exception:
        pass

    try:
        await client.ban_chat_member(message.chat.id, uid)
    except ChatAdminRequired:
        return await message.reply("❌ Give me ban rights first.")
    except UserAdminInvalid:
        return await message.reply("❌ Can't ban an admin.")

    name = user.first_name or str(uid)
    admin = message.from_user.first_name

    if EVENT_LOGS:
        try:
            await client.send_message(EVENT_LOGS,
                f"<b>#DBan</b>\n<b>User:</b> <a href='tg://user?id={uid}'>{name}</a> (<code>{uid}</code>)\n"
                f"<b>By:</b> {admin} | <b>Chat:</b> {message.chat.title}", parse_mode="html")
        except Exception:
            pass

    kb = InlineKeyboardMarkup([[
        InlineKeyboardButton("✅ Unban", callback_data=f"dban_unban_{uid}"),
        InlineKeyboardButton("🗑 Close", callback_data="dban_close"),
    ]])
    gif = await _gif()
    if gif:
        await message.reply_video(gif,
            caption=f"<u><b>🚫 DBan!</b></u>\n<b>User:</b> <a href='tg://user?id={uid}'>{name}</a>\n<b>By:</b> {admin}",
            reply_markup=kb)
    else:
        await message.reply(f"🚫 <b>DBanned</b> <a href='tg://user?id={uid}'>{name}</a>", reply_markup=kb)


@Client.on_message(custom_filter.command(commands=["sban"]))
async def sban_cmd(client: Client, message: Message):
    if not await isUserAdmin(message) and not await _elevated(message.from_user.id):
        return
    user = await get_user_id(message)
    if not user:
        return
    try:
        await message.delete()
    except Exception:
        pass
    if message.reply_to_message:
        try:
            await message.reply_to_message.delete()
        except Exception:
            pass
    try:
        await client.ban_chat_member(message.chat.id, user.id)
    except Exception:
        pass
    if EVENT_LOGS:
        try:
            name = user.first_name or str(user.id)
            await client.send_message(EVENT_LOGS,
                f"<b>#SBan</b>\n<b>User:</b> <a href='tg://user?id={user.id}'>{name}</a> (<code>{user.id}</code>)\n"
                f"<b>By:</b> {message.from_user.first_name} | <b>Chat:</b> {message.chat.title}", parse_mode="html")
        except Exception:
            pass


@Client.on_callback_query(filters.regex(r"^dban_unban_(\d+)$"))
async def dban_unban_cb(client: Client, cq):
    uid = int(cq.data.split("_")[2])
    try:
        await client.unban_chat_member(cq.message.chat.id, uid)
        await cq.answer("✅ Unbanned!", show_alert=True)
        await cq.message.edit_reply_markup(None)
    except Exception as e:
        await cq.answer(f"❌ {e}", show_alert=True)


@Client.on_callback_query(filters.regex(r"^dban_close$"))
async def dban_close_cb(_, cq):
    await cq.message.delete()
