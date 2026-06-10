from pyrogram import Client, enums

import Chutki.strings as strings
from Chutki import custom_filter
from Chutki.helper.chat_status import isUserCan
from Chutki.mongo.welcome_mongo import UnSetWelcome
from Chutki.pyro.connection.connection import connection
from Chutki.utils.decorators import *


@Client.on_message(custom_filter.command(commands="resetwelcome"))
@anonadmin_checker
async def ResetWelcome(client, message):
    if await connection(message) is not None:
        chat_id = await connection(message)
    else:
        chat_id = message.chat.id

    if (
        not str(chat_id).startswith("-100")
        and message.chat.type == enums.ChatType.PRIVATE
    ):
        return await message.reply(strings.is_pvt)

    if not await isUserCan(message, privileges="can_change_info"):
        return
    await UnSetWelcome(chat_id)
    await message.reply("The welcome message has been reset to default!", quote=True)
