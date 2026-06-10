import os
from pyrogram import Client
from pyrogram.enums import ChatType
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from bson.objectid import ObjectId

from Chutki import custom_filter, BOT_NAME, TOKEN, SUPPORT_CHAT, UPDATE_CHANNEL, START_PIC
from Chutki.anime.bot import get_anime, get_recommendations, auth_link_cmd, logout_cmd, get_additional_info, code_cmd
from Chutki.pyro.connection.connect import connectRedirect
from Chutki.pyro.greetings.captcha.button_captcha import buttonCaptchaRedirect
from Chutki.pyro.greetings.captcha.text_captcha import textCaptchaRedirect
from Chutki.pyro.notes.private_notes import note_redirect
from Chutki.pyro.rules.rules import rulesRedirect
from Chutki.utils.decorators import *
from Chutki.utils.helper import AUTH_USERS, get_btns
from Chutki.anime.bot import help_

START_TEXT = """
Welcome to [{} :3]({})

This bot give varieties of features such as
➩ Group Management
➩ Spammer Protection
➩ Fun like chatbot
➩ Ranking & AI System
➩ Anime Loaded Modules
➩ Inline Games

Use the buttons or /help to checkout even more!
"""


@Client.on_message(custom_filter.command(commands="start"))
@leavemute
@rate_limit(RATE_LIMIT_GENERAL)
async def starttt(client, message):
    if len(message.text.split()) == 1:
        if message.chat.type == ChatType.PRIVATE:
            buttons = [
                [InlineKeyboardButton("Help", callback_data="help_back")],
                [
                    InlineKeyboardButton("Support", url=f"https://t.me/{SUPPORT_CHAT}"),
                    InlineKeyboardButton("News", url=f"https://t.me/{UPDATE_CHANNEL}"),
                ],
                [InlineKeyboardButton("Source Code", url="https://github.com/ArshCypherZ/Chutki")],
            ]
            await message.reply_text(
                START_TEXT.format(BOT_NAME, START_PIC),
                reply_markup=InlineKeyboardMarkup(buttons),
                disable_web_page_preview=False,
            )
        else:
            await message.reply("Hey there, ping me in my PM to get help!")

    if len(message.text.split()) > 1:
        user = message.from_user.id
        chat = message.chat.id
        deep_cmd_list = (message.text.split()[1]).split("_")

        if startCheckQuery(message, StartQuery="captcha"):
            await buttonCaptchaRedirect(client, message)
            await textCaptchaRedirect(client, message)

        elif startCheckQuery(message, StartQuery="note"):
            await note_redirect(client, message)

        elif startCheckQuery(message, StartQuery="connect"):
            await connectRedirect(client, message)

        elif startCheckQuery(message, StartQuery="rules"):
            await rulesRedirect(message, client)

        elif startCheckQuery(message, StartQuery="anihelp"):
            await help_(client, message)

        elif startCheckQuery(message, StartQuery="auth"):
            await auth_link_cmd(client, message)

        elif startCheckQuery(message, StartQuery="logout"):
            await logout_cmd(client, message)

        elif deep_cmd_list[0] == "des":
            try:
                req = deep_cmd_list[3]
            except IndexError:
                req = "desc"
            pic, result = await get_additional_info(deep_cmd_list[2], deep_cmd_list[1], req)
            await client.send_photo(chat, pic)
            try:
                await client.send_message(chat, result.replace("~!", "").replace("!~", ""))
            except (TypeError, AttributeError):
                await client.send_message(chat, "No description available!!!")

        elif deep_cmd_list[0] == "anime":
            auth = False
            if await AUTH_USERS.find_one({"id": user}):
                auth = True
            result = await get_anime({"id": int(deep_cmd_list[1])}, user=user, auth=auth)
            pic, msg = result[0], result[1]
            buttons = get_btns("ANIME", result=result, user=user, auth=auth)
            await client.send_photo(chat, pic, caption=msg, reply_markup=buttons)

        elif deep_cmd_list[0] == "anirec":
            result = await get_recommendations(deep_cmd_list[1])
            await client.send_message(user, result, disable_web_page_preview=True)

        elif (message.text.split()[1]).split("_", 1)[0] == "code":
            if not os.environ.get("ANILIST_REDIRECT_URL"):
                return
            qry = (message.text.split()[1]).split("_", 1)[1]
            k = await AUTH_USERS.find_one({"_id": ObjectId(qry)})
            await code_cmd(k["code"], message)


def startCheckQuery(message, StartQuery=None) -> bool:
    if (
        StartQuery in message.text.split()[1].split("_")[0]
        and message.text.split()[1].split("_")[0] == StartQuery
    ):
        return True
    return False
    
