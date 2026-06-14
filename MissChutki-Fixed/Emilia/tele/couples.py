import random
from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.types import ChannelParticipantsSearch

from Emilia import telethn
from Emilia.custom_filter import register

__mod_name__ = "Couples"
__help__ = """
• `/couple` — Randomly pairs two members as a couple for the day! 💑
"""

_couple_cache = {}


@register(pattern="couple")
async def couple_cmd(event):
    if event.is_private:
        return await event.reply("Use this in a group!")

    chat_id = event.chat_id

    try:
        participants = await telethn(
            GetParticipantsRequest(chat_id, ChannelParticipantsSearch(""), 0, 200, 0)
        )
        members = [u for u in participants.users if not u.bot and not u.deleted]

        if len(members) < 2:
            return await event.reply("❌ Need at least 2 real members to make a couple!")

        p1, p2 = random.sample(members, 2)

        name1 = p1.first_name or "Unknown"
        name2 = p2.first_name or "Unknown"

        text = (
            f"💑 **Today's Couple:**\n\n"
            f"[{name1}](tg://user?id={p1.id}) ❤️ [{name2}](tg://user?id={p2.id})\n\n"
            "Congratulations! 🎉"
        )
        await event.reply(text)

    except Exception as e:
        await event.reply(f"❌ Error: {e}")
