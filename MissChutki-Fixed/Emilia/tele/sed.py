import re
from Emilia.custom_filter import register
from telethon import events

__mod_name__ = "Sed"
__help__ = """
**Sed (Find & Replace)**
Reply to a message with `s/find/replace/` to replace text.
**Example:** Reply with `s/hello/world/` to replace "hello" with "world".
Use `s/find/replace/g` to replace all occurrences.
"""


@register(pattern=r"s/(.*?)/(.*?)(?:/(g|i|gi|ig)?)?$")
async def sed_cmd(event):
    if not event.reply_to_message:
        return

    orig_text = event.reply_to_message.text or event.reply_to_message.caption
    if not orig_text:
        return

    try:
        find = event.pattern_match.group(1)
        replace = event.pattern_match.group(2)
        flags_str = event.pattern_match.group(3) or ""

        flags = 0
        count = 1
        if "i" in flags_str:
            flags |= re.IGNORECASE
        if "g" in flags_str:
            count = 0

        new_text = re.sub(find, replace, orig_text, count=count, flags=flags)

        if new_text == orig_text:
            return await event.reply("No changes made (pattern not found).")

        await event.reply(new_text)

    except re.error as e:
        await event.reply(f"❌ Invalid regex: {e}")
