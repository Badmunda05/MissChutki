from pyrogram import Client, filters
from pyrogram.errors import ChatAdminRequired, UserAdminInvalid
from pyrogram.types import ChatPermissions, Message

from Emilia import custom_filter
from Emilia.helper.chat_status import isUserAdmin, isBotAdmin
from Emilia.mongo.blacklist_stickers_mongo import (
    add_to_blacklist, remove_from_blacklist,
    get_blacklisted_stickers, is_sticker_blacklisted,
    get_bl_sticker_mode, set_bl_sticker_mode,
)

__mod_name__ = "Sticker Blacklist"
__help__ = """
**Sticker Blacklist** — Block specific sticker packs in groups (Admin only)

• `/blackliststicker` — Show all blacklisted sticker packs.
• `/addblackliststicker` [sticker set name or reply to sticker] — Add sticker pack to blacklist.
• `/unblackliststicker` [sticker set name or reply to sticker] — Remove from blacklist.
• `/blstickermode` [del/mute/kick/ban] — Set action when blacklisted sticker is sent.
  - `del` — Delete only (default)
  - `mute` — Delete + mute user
  - `kick` — Delete + kick user
  - `ban` — Delete + ban user
"""

MUTE_PERMS = ChatPermissions(can_send_messages=False)


@Client.on_message(custom_filter.command(commands=["blackliststicker", "blsticker"]))
async def list_bl_stickers(_, message: Message):
    chat_id = message.chat.id
    stickers = await get_blacklisted_stickers(chat_id)
    mode = await get_bl_sticker_mode(chat_id)
    if not stickers:
        return await message.reply("No sticker packs are blacklisted in this group.")
    text = f"**🚫 Blacklisted Sticker Packs** (mode: `{mode}`):\n\n"
    text += "\n".join(f"• `{s}`" for s in stickers)
    await message.reply(text)


@Client.on_message(custom_filter.command(commands=["addblackliststicker", "addblsticker"]))
async def add_bl_sticker(_, message: Message):
    if not await isUserAdmin(message):
        return await message.reply("❌ Admins only.")
    chat_id = message.chat.id

    set_name = None
    if message.reply_to_message and message.reply_to_message.sticker:
        set_name = message.reply_to_message.sticker.set_name
    elif len(message.command) > 1:
        set_name = message.command[1]

    if not set_name:
        return await message.reply("Reply to a sticker or give the sticker pack name.\n**Usage:** `/addblackliststicker <pack_name>` or reply to a sticker.")

    if await is_sticker_blacklisted(chat_id, set_name):
        return await message.reply(f"Pack `{set_name}` is already blacklisted.")

    await add_to_blacklist(chat_id, set_name)
    await message.reply(f"✅ Sticker pack `{set_name}` added to blacklist!")


@Client.on_message(custom_filter.command(commands=["unblackliststicker", "unblsticker"]))
async def rm_bl_sticker(_, message: Message):
    if not await isUserAdmin(message):
        return await message.reply("❌ Admins only.")
    chat_id = message.chat.id

    set_name = None
    if message.reply_to_message and message.reply_to_message.sticker:
        set_name = message.reply_to_message.sticker.set_name
    elif len(message.command) > 1:
        set_name = message.command[1]

    if not set_name:
        return await message.reply("Reply to a sticker or give the sticker pack name.")

    if not await is_sticker_blacklisted(chat_id, set_name):
        return await message.reply(f"Pack `{set_name}` is not blacklisted.")

    await remove_from_blacklist(chat_id, set_name)
    await message.reply(f"✅ Sticker pack `{set_name}` removed from blacklist.")


@Client.on_message(custom_filter.command(commands=["blstickermode"]))
async def bl_sticker_mode(_, message: Message):
    if not await isUserAdmin(message):
        return await message.reply("❌ Admins only.")

    if len(message.command) < 2:
        mode = await get_bl_sticker_mode(message.chat.id)
        return await message.reply(f"Current blacklist sticker mode: `{mode}`\nOptions: `del`, `mute`, `kick`, `ban`")

    mode = message.command[1].lower()
    if mode not in ("del", "mute", "kick", "ban"):
        return await message.reply("❌ Invalid mode. Choose: `del`, `mute`, `kick`, `ban`")

    await set_bl_sticker_mode(message.chat.id, mode)
    await message.reply(f"✅ Blacklist sticker mode set to `{mode}`.")


# ─── WATCHER ───────────────────────────────────────────────────
@Client.on_message(filters.group & filters.sticker, group=4)
async def bl_sticker_watcher(client: Client, message: Message):
    if not message.sticker or not message.sticker.set_name:
        return

    chat_id = message.chat.id
    set_name = message.sticker.set_name

    if not await is_sticker_blacklisted(chat_id, set_name):
        return

    # Skip admins
    if await isUserAdmin(message):
        return

    mode = await get_bl_sticker_mode(chat_id)
    user_id = message.from_user.id

    try:
        await message.delete()
    except Exception:
        pass

    try:
        if mode == "mute":
            await client.restrict_chat_member(chat_id, user_id, MUTE_PERMS)
            await message.reply(f"🔇 {message.from_user.mention} muted for sending a blacklisted sticker pack.")
        elif mode == "kick":
            await client.ban_chat_member(chat_id, user_id)
            await client.unban_chat_member(chat_id, user_id)
            await message.reply(f"👢 {message.from_user.mention} kicked for sending a blacklisted sticker pack.")
        elif mode == "ban":
            await client.ban_chat_member(chat_id, user_id)
            await message.reply(f"🚫 {message.from_user.mention} banned for sending a blacklisted sticker pack.")
        # del mode: already deleted, no further action
    except (ChatAdminRequired, UserAdminInvalid):
        pass
