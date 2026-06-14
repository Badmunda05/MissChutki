import time
import platform
import sys
from datetime import datetime, timezone

import psutil
from telethon import __version__ as tl_version

from Emilia import telethn, BOT_USERNAME
from Emilia.custom_filter import register

__mod_name__ = "Alive"
__help__ = """
• `/alive` — Check if the bot is running and see stats.
• `/ping` is also available in the ping module.
"""

_start_time = time.time()


@register(pattern="alive")
async def alive_cmd(event):
    uptime_seconds = int(time.time() - _start_time)
    hours, remainder = divmod(uptime_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    uptime_str = f"{hours}h {minutes}m {seconds}s"

    cpu = psutil.cpu_percent(interval=1)
    mem = psutil.virtual_memory()
    mem_used = round(mem.used / (1024 ** 3), 2)
    mem_total = round(mem.total / (1024 ** 3), 2)

    text = (
        f"**🌸 {BOT_USERNAME} is Alive!**\n\n"
        f"⏱ **Uptime:** `{uptime_str}`\n"
        f"🐍 **Python:** `{sys.version.split()[0]}`\n"
        f"📚 **Telethon:** `{tl_version}`\n"
        f"💻 **CPU:** `{cpu}%`\n"
        f"🧠 **RAM:** `{mem_used} GB / {mem_total} GB`\n"
        f"🖥 **Platform:** `{platform.system()} {platform.release()}`"
    )

    await event.reply(text)
