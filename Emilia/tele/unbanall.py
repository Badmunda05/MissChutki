import asyncio
from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.types import ChannelParticipantsKicked, ChannelParticipantBanned

from Emilia import telethn, OWNER_ID, DEV_USERS
from Emilia.custom_filter import register

__mod_name__ = "UnBan All"
__help__ = """
• `/unbanall` — Unban all banned users from the group. (Admin only)
"""


@register(pattern="unbanall")
async def unbanall_cmd(event):
    if event.is_private:
        return await event.reply("Use this command in a group.")

    perm = await event.client.get_permissions(event.chat_id, event.sender_id)
    if not (perm.is_admin or event.sender_id in DEV_USERS or event.sender_id == OWNER_ID):
        return await event.reply("❌ You need to be an admin to use this.")

    msg = await event.reply("⏳ Unbanning all banned users...")

    try:
        count = 0
        offset = 0
        limit = 100
        while True:
            banned = await telethn(
                GetParticipantsRequest(
                    event.chat_id,
                    ChannelParticipantsKicked(""),
                    offset,
                    limit,
                    0,
                )
            )
            if not banned.users:
                break
            for user in banned.users:
                try:
                    await telethn.edit_permissions(event.chat_id, user.id, view_messages=True)
                    count += 1
                    await asyncio.sleep(0.3)
                except Exception:
                    pass
            offset += len(banned.users)

        await msg.edit(f"✅ Successfully unbanned **{count}** users.")
    except Exception as e:
        await msg.edit(f"❌ Error: {e}")
