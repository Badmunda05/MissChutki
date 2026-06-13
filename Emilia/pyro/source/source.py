import sys
import pyrogram
import telethon

from pyrogram import Client
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from Emilia import custom_filter

__mod_name__ = "Source"
__help__ = """
• `/repo` or `/source` — Show bot info, versions and GitHub link.
"""

REPO_URL = "https://github.com/Spiral-Void/MissChutki"


@Client.on_message(custom_filter.command(commands=["repo", "source"]))
async def source_cmd(client: Client, message: Message):
    bot = await client.get_me()
    text = (
        f"**🌸 {bot.first_name}**\n\n"
        f"🐍 **Python:** `{sys.version.split()[0]}`\n"
        f"📦 **Pyrogram:** `{pyrogram.__version__}`\n"
        f"📡 **Telethon:** `{telethon.__version__}`\n\n"
        f"Made with ❤️"
    )
    await message.reply(
        text,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔗 GitHub Repo", url=REPO_URL)],
            [InlineKeyboardButton("👨‍💻 Developer", url="https://t.me/SpiralVoid")],
        ])
    )
