import os
import orjson


def get_user_list(config, key):
    with open("{}/Chutki/{}".format(os.getcwd(), config), "rb") as json_file:
        return orjson.loads(json_file.read())[key]


class Config(object):
    # --- Telegram API ---
    API_ID = int(os.getenv("API_ID", 0))
    API_HASH = os.getenv("API_HASH", "")

    # --- Bot Credentials ---
    TOKEN = os.getenv("TOKEN", "")
    BOT_ID = int(os.getenv("BOT_ID", 0))
    BOT_USERNAME = os.getenv("BOT_USERNAME", "")
    BOT_NAME = os.getenv("BOT_NAME", "Emilia")

    # --- MongoDB ---
    MONGO_DB_URL = os.getenv("MONGO_DB_URL", "")

    # --- Owner / Dev ---
    OWNER_ID = int(os.getenv("OWNER_ID", 0))
    DEV_USERS = [
        int(x) for x in os.getenv("DEV_USERS", "0").split(",") if x.strip().isdigit()
    ]

    # --- Logs & Support ---
    EVENT_LOGS = int(os.getenv("EVENT_LOGS", 0))
    SUPPORT_CHAT = os.getenv("SUPPORT_CHAT", "")
    UPDATE_CHANNEL = os.getenv("UPDATE_CHANNEL", "")

    # --- Bot Settings ---
    START_PIC = os.getenv("START_PIC", "")
    TEMP_DOWNLOAD_DIRECTORY = os.getenv("TEMP_DOWNLOAD_DIRECTORY", "./")

    # --- External APIs ---
    WALL_API = os.getenv("WALL_API", "")
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")


class Production(Config):
    LOGGER = True


class Development(Config):
    LOGGER = True
    
