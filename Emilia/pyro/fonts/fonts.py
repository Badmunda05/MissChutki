from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

from Emilia import custom_filter
from Emilia.utils.fonts import Fonts

__mod_name__ = "Font Editor"
__help__ = """
• `/font` [text] — Convert text to 39+ fancy Unicode font styles with interactive buttons.
**Example:** `/font Hello World`
"""

FONT_BUTTONS_PAGE1 = InlineKeyboardMarkup([
    [
        InlineKeyboardButton("𝚃𝚢𝚙𝚎𝚠𝚛𝚒𝚝𝚎𝚛", callback_data="font+typewriter"),
        InlineKeyboardButton("𝕆𝕦𝕥𝕝𝕚𝕟𝕖", callback_data="font+outline"),
        InlineKeyboardButton("𝐒𝐞𝐫𝐢𝐟", callback_data="font+serif"),
    ],
    [
        InlineKeyboardButton("𝑺𝒆𝒓𝒊𝒇", callback_data="font+bold_cool"),
        InlineKeyboardButton("𝑆𝑒𝑟𝑖𝑓", callback_data="font+cool"),
        InlineKeyboardButton("Sᴍᴀʟʟ Cᴀᴘs", callback_data="font+small_cap"),
    ],
    [
        InlineKeyboardButton("𝓈𝒸𝓇𝒾𝓅𝓉", callback_data="font+script"),
        InlineKeyboardButton("𝓼𝓬𝓻𝓲𝓹𝓽", callback_data="font+script_bolt"),
        InlineKeyboardButton("ᵗⁱⁿʸ", callback_data="font+tiny"),
    ],
    [
        InlineKeyboardButton("ᑕOᗰIᑕ", callback_data="font+comic"),
        InlineKeyboardButton("𝗦𝗮𝗻𝘀", callback_data="font+sans"),
        InlineKeyboardButton("𝙎𝙖𝙣𝙨", callback_data="font+slant_sans"),
    ],
    [
        InlineKeyboardButton("𝘚𝘢𝘯𝘴", callback_data="font+slant"),
        InlineKeyboardButton("𝖲𝖺𝗇𝗌", callback_data="font+sim"),
        InlineKeyboardButton("Ⓒ︎Ⓘ︎Ⓡ︎Ⓒ︎Ⓛ︎Ⓔ︎Ⓢ︎", callback_data="font+circles"),
    ],
    [
        InlineKeyboardButton("🅒︎🅘︎🅡︎🅒︎🅛︎🅔︎🅢︎", callback_data="font+circle_dark"),
        InlineKeyboardButton("𝔊𝔬𝔱𝔥𝔦𝔠", callback_data="font+gothic"),
        InlineKeyboardButton("𝕲𝖔𝖙𝖍𝖎𝖈", callback_data="font+gothic_bolt"),
    ],
    [
        InlineKeyboardButton("C͜͡l͜͡o͜͡u͜͡d͜͡s͜͡", callback_data="font+cloud"),
        InlineKeyboardButton("H̆̈ă̈p̆̈p̆̈y̆̈", callback_data="font+happy"),
        InlineKeyboardButton("S̑̈ȃ̈d̑̈", callback_data="font+sad"),
    ],
    [InlineKeyboardButton("ɴᴇxᴛ ➻", callback_data="font_page+2")],
])

FONT_BUTTONS_PAGE2 = InlineKeyboardMarkup([
    [
        InlineKeyboardButton("🇸 🇵 🇪 🇨 🇮 🇦 🇱", callback_data="font+special"),
        InlineKeyboardButton("🅂🅀🅄🄰🅁🄴🅂", callback_data="font+squares"),
        InlineKeyboardButton("🆂︎🆀︎🆄︎🅰︎🆁︎🅴︎🆂︎", callback_data="font+squares_bold"),
    ],
    [
        InlineKeyboardButton("ꪖꪀᦔꪖꪶꪊᥴ𝓲ꪖ", callback_data="font+andalucia"),
        InlineKeyboardButton("爪卂几ᘜ卂", callback_data="font+manga"),
        InlineKeyboardButton("S̾t̾i̾n̾k̾y̾", callback_data="font+stinky"),
    ],
    [
        InlineKeyboardButton("B̥ͦu̥ͦb̥ͦb̥ͦl̥ͦe̥ͦs̥ͦ", callback_data="font+bubbles"),
        InlineKeyboardButton("U͟n͟d͟e͟r͟l͟i͟n͟e͟", callback_data="font+underline"),
        InlineKeyboardButton("꒒ꍏꀷꌩꌷꀎꁅ", callback_data="font+ladybug"),
    ],
    [
        InlineKeyboardButton("R҉a҉y҉s҉", callback_data="font+rays"),
        InlineKeyboardButton("B҈i҈r҈d҈s҈", callback_data="font+birds"),
        InlineKeyboardButton("S̸l̸a̸s̸h̸", callback_data="font+slash"),
    ],
    [
        InlineKeyboardButton("s⃠t⃠o⃠p⃠", callback_data="font+stop"),
        InlineKeyboardButton("S̺͆k̺͆y̺͆l̺͆i̺͆n̺͆e̺͆", callback_data="font+skyline"),
        InlineKeyboardButton("A͎r͎r͎o͎w͎s͎", callback_data="font+arrows"),
    ],
    [
        InlineKeyboardButton("ዪሀክቿነ", callback_data="font+qvnes"),
        InlineKeyboardButton("S̶t̶r̶i̶k̶e̶", callback_data="font+strike"),
        InlineKeyboardButton("F༙r༙o༙z༙e༙n༙", callback_data="font+frozen"),
    ],
    [InlineKeyboardButton("◀ ʙᴀᴄᴋ", callback_data="font_page+1")],
])

STYLE_MAP = {
    "typewriter": Fonts.typewriter, "outline": Fonts.outline, "serif": Fonts.serief,
    "bold_cool": Fonts.bold_cool, "cool": Fonts.cool, "small_cap": Fonts.smallcap,
    "script": Fonts.script, "script_bolt": Fonts.bold_script, "tiny": Fonts.tiny,
    "comic": Fonts.comic, "sans": Fonts.san, "slant_sans": Fonts.slant_san,
    "slant": Fonts.slant, "sim": Fonts.sim, "circles": Fonts.circles,
    "circle_dark": Fonts.dark_circle, "gothic": Fonts.gothic, "gothic_bolt": Fonts.bold_gothic,
    "cloud": Fonts.cloud, "happy": Fonts.happy, "sad": Fonts.sad,
    "special": Fonts.special, "squares": Fonts.square, "squares_bold": Fonts.dark_square,
    "andalucia": Fonts.andalucia, "manga": Fonts.manga, "stinky": Fonts.stinky,
    "bubbles": Fonts.bubbles, "underline": Fonts.underline, "ladybug": Fonts.ladybug,
    "rays": Fonts.rays, "birds": Fonts.birds, "slash": Fonts.slash,
    "stop": Fonts.stop, "skyline": Fonts.skyline, "arrows": Fonts.arrows,
    "qvnes": Fonts.rvnes, "strike": Fonts.strike, "frozen": Fonts.frozen,
}


@Client.on_message(custom_filter.command(commands=["font", "fonts"]))
async def font_cmd(_, message: Message):
    args = message.command
    if len(args) < 2:
        return await message.reply(
            "Give me some text to style!\n**Usage:** `/font Hello World`"
        )
    text = " ".join(args[1:])
    await message.reply(
        text,
        reply_markup=FONT_BUTTONS_PAGE1,
    )


@Client.on_callback_query(filters.regex(r"^font_page\+(\d)$"))
async def font_page(_, query: CallbackQuery):
    page = query.data.split("+")[1]
    await query.answer()
    if page == "2":
        await query.message.edit_reply_markup(FONT_BUTTONS_PAGE2)
    else:
        await query.message.edit_reply_markup(FONT_BUTTONS_PAGE1)


@Client.on_callback_query(filters.regex(r"^font\+(.+)$"))
async def font_style(_, query: CallbackQuery):
    style = query.data.split("+", 1)[1]
    await query.answer()

    original = query.message.text or query.message.caption
    if not original:
        return

    func = STYLE_MAP.get(style)
    if not func:
        return

    try:
        new_text = func(original)
        await query.message.edit_text(
            new_text,
            reply_markup=query.message.reply_markup
        )
    except Exception:
        pass
