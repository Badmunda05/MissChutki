from pyrogram import Client, enums

import Chutki.strings as strings
from Chutki import custom_filter
from Chutki.helper.chat_status import isUserCan
from Chutki.helper.welcome_helper.get_welcome_message import GetWelcomeMessage
from Chutki.mongo.welcome_mongo import SetGoodBye
from Chutki.pyro.connection.connection import connection
from Chutki.utils.decorators import *


@Client.on_message(custom_filter.command(commands="setgoodbye"))
@anonadmin_checker
async def set_goodbye(client, message):
    if await connection(message) is not None:
        ChatID = await connection(message)
    else:
        ChatID = message.chat.id

    if (
        not str(ChatID).startswith("-100")
        and message.chat.type == enums.ChatType.PRIVATE
    ):
        return await message.reply(strings.is_pvt)

    if not await isUserCan(message, privileges="can_change_info"):
        return

    command = message.text.split(" ")
    if not message.reply_to_message and len(command) == 1:
        return await message.reply("You need to give the goodbye message some content!")

    CONTENT, TEXT, DATATYPE = GetWelcomeMessage(message)
    await SetGoodBye(ChatID, CONTENT, TEXT, DATATYPE)
    await message.reply("The new goodbye message has been saved!", quote=True)
