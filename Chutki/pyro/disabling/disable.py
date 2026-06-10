from pyrogram import Client, enums

import Chutki.strings as strings
from Chutki import custom_filter
from Chutki.custom_filter import DISABLE_COMMANDS
from Chutki.helper.chat_status import check_user
from Chutki.mongo.disable_mongo import disable_db
from Chutki.pyro.connection.connection import connection
from Chutki.utils.decorators import *


@usage("/disable [command]")
@example("/disable notes")
@description(
    "Use this command to disable another command for users. Check the command that can be disabled through /disableable."
)
@Client.on_message(custom_filter.command(commands="disable"))
async def disable(client, message):
    if await connection(message) is not None:
        chat_id = await connection(message)
    else:
        chat_id = message.chat.id

    if (
        not str(chat_id).startswith("-100")
        and message.chat.type == enums.ChatType.PRIVATE
    ):
        return await message.reply(strings.is_pvt)

    if not await check_user(message, privileges="can_change_info"):
        return

    if not (len(message.text.split()) >= 2):
        await usage_string(message, disable)
        return

    disable_args = message.text.split()[1:]

    DISABLE_ITMES = []
    INCORRECT_ITEMS = []

    for disable_arg in disable_args:
        if disable_arg not in DISABLE_COMMANDS:
            INCORRECT_ITEMS.append(disable_arg)
        else:
            DISABLE_ITMES.append(disable_arg)

    if len(INCORRECT_ITEMS) != 0:
        text = "Unknown command to disable:\n"
        for item in INCORRECT_ITEMS:
            text += f"- `{item}`\n"
        text += "Check /disableable!"
        await message.reply(text)
        return

    for items in DISABLE_ITMES:
        await disable_db(chat_id, items)

    text = "Disabled:\n"
    for disable_arg in DISABLE_ITMES:
        if len(DISABLE_ITMES) != 1:
            text += f"- `{disable_arg}`\n"
        else:
            text = f"Disabled `{disable_arg}`."

    await message.reply(text)
