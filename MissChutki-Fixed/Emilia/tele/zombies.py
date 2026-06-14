import asyncio
from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.types import ChannelParticipantsSearch

from Emilia import telethn, OWNER_ID, DEV_USERS
from Emilia.custom_filter import register

__mod_name__ = "Zombies"
__help__ = """
• `/zombies` — Scan and kick deleted Telegram accounts from the group.
• `/zombies scan` — Only scan without kicking.
"""


@register(pattern="zombies(?: (.+))?")
async def zombies_cmd(event):
    if event.is_private:
        return await event.reply("Use this command in a group.")

    match = event.pattern_match.group(1)
    scan_only = match and match.strip().lower() == "scan"

    perm = await event.client.get_permissions(event.chat_id, event.sender_id)
    if not (perm.is_admin or event.sender_id in DEV_USERS or event.sender_id == OWNER_ID):
        return await event.reply("❌ You need to be an admin to use this.")

    msg = await event.reply("🧟 Scanning for zombie accounts...")

    try:
        zombies = []
        offset = 0
        limit = 200

        while True:
            participants = await telethn(
                GetParticipantsRequest(
                    event.chat_id, ChannelParticipantsSearch(""), offset, limit, 0
                )
            )
            if not participants.users:
                break
            for user in participants.users:
                if user.deleted:
                    zombies.append(user.id)
            offset += len(participants.users)
            if len(participants.users) < limit:
                break

        if not zombies:
            return await msg.edit("✅ No zombie accounts found!")

        if scan_only:
            return await msg.edit(f"🧟 Found **{len(zombies)}** zombie accounts. Use `/zombies` to kick them.")

        kicked = 0
        for uid in zombies:
            try:
                await telethn.kick_participant(event.chat_id, uid)
                kicked += 1
                await asyncio.sleep(0.3)
            except Exception:
                pass

        await msg.edit(f"✅ Kicked **{kicked}/{len(zombies)}** zombie accounts.")

    except Exception as e:
        await msg.edit(f"❌ Error: {e}")
