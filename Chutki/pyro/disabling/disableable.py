from pyrogram import Client

from Chutki import custom_filter
from Chutki.custom_filter import DISABLE_COMMANDS
from Chutki.helper.chat_status import isUserAdmin


@Client.on_message(custom_filter.command(commands="disableable"))
async def disable_list(client, message):
    if not await isUserAdmin(message):
        return

    text_header = "The following commands can be disabled:\n"
    for diable in DISABLE_COMMANDS:
        text_header += f"- `{diable}`\n"

    await message.reply(text_header, quote=True)
