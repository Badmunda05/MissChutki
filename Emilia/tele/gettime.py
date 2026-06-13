from datetime import datetime
import pytz
from Emilia.custom_filter import register

__mod_name__ = "Get Time"
__help__ = """
• `/time` [timezone] — Get current time in any timezone.
**Example:** `/time Asia/Kolkata` or `/time America/New_York`
"""


@register(pattern="time(?: (.+))?")
async def gettime_cmd(event):
    match = event.pattern_match.group(1)
    if not match:
        return await event.reply(
            "**Usage:** `/time Asia/Kolkata`\n\nCommon: `UTC`, `Asia/Kolkata`, `America/New_York`, `Europe/London`"
        )

    tz_name = match.strip()
    try:
        tz = pytz.timezone(tz_name)
        now = datetime.now(tz)
        await event.reply(
            f"🕐 **Time in {tz_name}:**\n`{now.strftime('%Y-%m-%d %H:%M:%S %Z')}`"
        )
    except pytz.exceptions.UnknownTimeZoneError:
        await event.reply(f"❌ Unknown timezone: `{tz_name}`\nTry something like `Asia/Kolkata` or `UTC`.")
