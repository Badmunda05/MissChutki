import html
from pyrogram import Client
from pyrogram.types import Message

from Emilia import OWNER_ID, DEV_USERS, custom_filter
from Emilia.helper.get_user import get_user_id
from Emilia.mongo.disasters_mongo import (
    add_dragon, remove_dragon, is_dragon, get_dragons,
    add_demon,  remove_demon,  is_demon,  get_demons,
    add_tiger,  remove_tiger,  is_tiger,  get_tigers,
    add_wolf,   remove_wolf,   is_wolf,   get_wolves,
)

__mod_name__ = "Disasters"
__help__ = """
**Elevated Users System** — Owner only

**🐉 Dragons (Sudo)** — Full bot powers
• `/addsudo` — Add a Dragon
• `/rmsudo` — Remove a Dragon
• `/sudolist` — List all Dragons

**👹 Demons (Support)** — Moderate powers (can gban etc)
• `/addsupport` — Add a Demon
• `/rmsupport` — Remove a Demon
• `/supportlist` — List all Demons

**🐯 Tigers** — Limited elevated powers
• `/addtiger` — Add a Tiger
• `/rmtiger` — Remove a Tiger
• `/tigerlist` — List all Tigers

**🐺 Wolves (Whitelist)** — Immune to gban/gmute/auto-actions
• `/addwhitelist` — Add a Wolf
• `/rmwhitelist` — Remove a Wolf
• `/whitelistlist` — List all Wolves

• `/devlist` — Show all elevated users at once
"""


def _is_owner(uid: int) -> bool:
    return uid == OWNER_ID or uid in DEV_USERS


async def _fmt_user(user) -> str:
    if not user:
        return "Unknown"
    name = html.escape(user.first_name or "")
    return f"<a href='tg://user?id={user.id}'>{name}</a> (<code>{user.id}</code>)"


# ─── DRAGONS ────────────────────────────────────────────────────

@Client.on_message(custom_filter.command(commands=["addsudo", "adddragons"]))
async def add_sudo(client: Client, message: Message):
    if not _is_owner(message.from_user.id):
        return await message.reply("❌ Only the **Owner** can add sudo users.")
    user = await get_user_id(message)
    if not user:
        return await message.reply("Can't find that user.")
    if user.id == OWNER_ID:
        return await message.reply("That's already the owner!")
    if await is_dragon(user.id):
        return await message.reply("Already a Dragon 🐉")
    await add_dragon(user.id)
    await message.reply(f"🐉 {await _fmt_user(user)} is now a **Dragon (Sudo)**!", parse_mode="html")


@Client.on_message(custom_filter.command(commands=["rmsudo", "removedragons"]))
async def rm_sudo(client: Client, message: Message):
    if not _is_owner(message.from_user.id):
        return await message.reply("❌ Only the **Owner** can remove sudo users.")
    user = await get_user_id(message)
    if not user:
        return await message.reply("Can't find that user.")
    if not await is_dragon(user.id):
        return await message.reply("This user is not a Dragon.")
    await remove_dragon(user.id)
    await message.reply(f"✅ {await _fmt_user(user)} removed from **Dragons**.", parse_mode="html")


@Client.on_message(custom_filter.command(commands=["sudolist", "dragons"]))
async def sudo_list(client: Client, message: Message):
    ids = await get_dragons()
    if not ids:
        return await message.reply("No Dragons yet 🐉")
    lines = ["**🐉 Dragons (Sudo Users):**\n"]
    for uid in ids:
        try:
            u = await client.get_users(uid)
            lines.append(f"• {await _fmt_user(u)}")
        except Exception:
            lines.append(f"• <code>{uid}</code>")
    await message.reply("\n".join(lines), parse_mode="html")


# ─── DEMONS ─────────────────────────────────────────────────────

@Client.on_message(custom_filter.command(commands=["addsupport", "adddemons"]))
async def add_support(client: Client, message: Message):
    if not _is_owner(message.from_user.id):
        return await message.reply("❌ Only the **Owner** can add support users.")
    user = await get_user_id(message)
    if not user:
        return await message.reply("Can't find that user.")
    if await is_demon(user.id):
        return await message.reply("Already a Demon 👹")
    await add_demon(user.id)
    await message.reply(f"👹 {await _fmt_user(user)} is now a **Demon (Support)**!", parse_mode="html")


@Client.on_message(custom_filter.command(commands=["rmsupport", "removedemons"]))
async def rm_support(client: Client, message: Message):
    if not _is_owner(message.from_user.id):
        return await message.reply("❌ Only the **Owner** can remove support users.")
    user = await get_user_id(message)
    if not user:
        return await message.reply("Can't find that user.")
    if not await is_demon(user.id):
        return await message.reply("This user is not a Demon.")
    await remove_demon(user.id)
    await message.reply(f"✅ {await _fmt_user(user)} removed from **Demons**.", parse_mode="html")


@Client.on_message(custom_filter.command(commands=["supportlist", "demons"]))
async def support_list(client: Client, message: Message):
    ids = await get_demons()
    if not ids:
        return await message.reply("No Demons yet 👹")
    lines = ["**👹 Demons (Support Users):**\n"]
    for uid in ids:
        try:
            u = await client.get_users(uid)
            lines.append(f"• {await _fmt_user(u)}")
        except Exception:
            lines.append(f"• <code>{uid}</code>")
    await message.reply("\n".join(lines), parse_mode="html")


# ─── TIGERS ─────────────────────────────────────────────────────

@Client.on_message(custom_filter.command(commands=["addtiger", "tigers"]))
async def add_tiger_cmd(client: Client, message: Message):
    if not _is_owner(message.from_user.id):
        return await message.reply("❌ Only the **Owner** can add tigers.")
    user = await get_user_id(message)
    if not user:
        return await message.reply("Can't find that user.")
    if await is_tiger(user.id):
        return await message.reply("Already a Tiger 🐯")
    await add_tiger(user.id)
    await message.reply(f"🐯 {await _fmt_user(user)} is now a **Tiger**!", parse_mode="html")


@Client.on_message(custom_filter.command(commands=["rmtiger", "removetiger"]))
async def rm_tiger_cmd(client: Client, message: Message):
    if not _is_owner(message.from_user.id):
        return await message.reply("❌ Only the **Owner** can remove tigers.")
    user = await get_user_id(message)
    if not user:
        return await message.reply("Can't find that user.")
    if not await is_tiger(user.id):
        return await message.reply("This user is not a Tiger.")
    await remove_tiger(user.id)
    await message.reply(f"✅ {await _fmt_user(user)} removed from **Tigers**.", parse_mode="html")


@Client.on_message(custom_filter.command(commands=["tigerlist"]))
async def tiger_list(client: Client, message: Message):
    ids = await get_tigers()
    if not ids:
        return await message.reply("No Tigers yet 🐯")
    lines = ["**🐯 Tigers:**\n"]
    for uid in ids:
        try:
            u = await client.get_users(uid)
            lines.append(f"• {await _fmt_user(u)}")
        except Exception:
            lines.append(f"• <code>{uid}</code>")
    await message.reply("\n".join(lines), parse_mode="html")


# ─── WOLVES ─────────────────────────────────────────────────────

@Client.on_message(custom_filter.command(commands=["addwhitelist", "wolves"]))
async def add_wolf_cmd(client: Client, message: Message):
    if not _is_owner(message.from_user.id):
        return await message.reply("❌ Only the **Owner** can whitelist users.")
    user = await get_user_id(message)
    if not user:
        return await message.reply("Can't find that user.")
    if await is_wolf(user.id):
        return await message.reply("Already a Wolf 🐺")
    await add_wolf(user.id)
    await message.reply(f"🐺 {await _fmt_user(user)} added to **Wolves (Whitelist)**!\nThey are immune to auto-actions.", parse_mode="html")


@Client.on_message(custom_filter.command(commands=["rmwhitelist", "removewolf"]))
async def rm_wolf_cmd(client: Client, message: Message):
    if not _is_owner(message.from_user.id):
        return await message.reply("❌ Only the **Owner** can remove whitelist.")
    user = await get_user_id(message)
    if not user:
        return await message.reply("Can't find that user.")
    if not await is_wolf(user.id):
        return await message.reply("This user is not a Wolf.")
    await remove_wolf(user.id)
    await message.reply(f"✅ {await _fmt_user(user)} removed from **Wolves**.", parse_mode="html")


@Client.on_message(custom_filter.command(commands=["whitelistlist", "wolflist"]))
async def wolf_list(client: Client, message: Message):
    ids = await get_wolves()
    if not ids:
        return await message.reply("No Wolves yet 🐺")
    lines = ["**🐺 Wolves (Whitelist):**\n"]
    for uid in ids:
        try:
            u = await client.get_users(uid)
            lines.append(f"• {await _fmt_user(u)}")
        except Exception:
            lines.append(f"• <code>{uid}</code>")
    await message.reply("\n".join(lines), parse_mode="html")


# ─── DEVLIST (ALL IN ONE) ───────────────────────────────────────

@Client.on_message(custom_filter.command(commands=["devlist", "elevated"]))
async def dev_list(client: Client, message: Message):
    async def get_names(ids):
        names = []
        for uid in ids:
            try:
                u = await client.get_users(uid)
                names.append(f"• {await _fmt_user(u)}")
            except Exception:
                names.append(f"• <code>{uid}</code>")
        return names or ["• None"]

    d = await get_names(await get_dragons())
    dm = await get_names(await get_demons())
    t = await get_names(await get_tigers())
    w = await get_names(await get_wolves())

    text = (
        "**👑 Elevated Users:**\n\n"
        f"**🐉 Dragons (Sudo):**\n" + "\n".join(d) + "\n\n"
        f"**👹 Demons (Support):**\n" + "\n".join(dm) + "\n\n"
        f"**🐯 Tigers:**\n" + "\n".join(t) + "\n\n"
        f"**🐺 Wolves (Whitelist):**\n" + "\n".join(w)
    )
    await message.reply(text, parse_mode="html")
