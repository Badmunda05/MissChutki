import orjson
import os


def get_user_list(config, key):
    with open("{}/Emilia/{}".format(os.getcwd(), config), "rb") as json_file:
        return orjson.loads(json_file.read())[key]

class Config(object):
    API_HASH = "b35b715fe8dc0a58e8048988286fc5b6" # API_HASH from my.telegram.org
    API_ID = 25742938 # API_ID from my.telegram.org

    BOT_ID = 8786133106 # BOT_ID
    BOT_USERNAME = "MissChutki_Bot" # BOT_USERNAME

    MONGO_DB_URL = "mongodb+srv://PurviBots:PublicMongo@cluster0.gy2adez.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0" # MongoDB URL from MongoDB Atlas

    SUPPORT_CHAT = "PBXCHATS" # Support Chat Username
    UPDATE_CHANNEL = "PBX_UPDATE" # Update Channel Username
    START_PIC = "https://pic-bstarstatic.akamaized.net/ugc/9e98b6c8872450f3e8b19e0d0aca02deff02981f.jpg@1200w_630h_1e_1c_1f.webp" # Start Image
    DEV_USERS = [7616808278] # Dev Users
    TOKEN = "8786133106:AAE2O6cR6HJWPPpe-Spukj3HaRNkmABd27k" # Bot Token from @BotFather

    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
    REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", None)

    EVENT_LOGS = -1003758847277 # Event Logs Chat ID
    OWNER_ID = 7616808278 # Owner ID
 
    TEMP_DOWNLOAD_DIRECTORY = "./" # Temporary Download Directory
    BOT_NAME = "🌸 MissChutki" # Bot Name
    WALL_API = "6950f53" # Wall API from wall.alphacoders.com
    GROQ_API_KEY = "gsk_mm" # GROQ API Key from groq.com



    UPSTREAM_REPO = "https://github.com/Spiral-Void/MissChutki"  # Your GitHub repo URL
    UPSTREAM_BRANCH = "main"                                       # Branch to pull from
    GIT_TOKEN = None                                               # Fill if repo is private

class Production(Config):
    LOGGER = True


class Development(Config):
    LOGGER = True
