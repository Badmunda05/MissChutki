"""
Elevated users system:
- Dragons (Sudo) — full bot powers
- Demons (Support) — limited sudo, can gban etc
- Tigers — can use some sudo commands
- Wolves (Whitelist) — gban/gmute immune, can't be banned by bot
"""
from Emilia import db

dragons_col = db["dragons"]   # sudo users
demons_col  = db["demons"]    # support users
tigers_col  = db["tigers"]    # tiger users
wolves_col  = db["wolves"]    # whitelist users


# ── DRAGONS (SUDO) ─────────────────────────────────────────────
async def add_dragon(user_id: int):
    await dragons_col.update_one({"uid": user_id}, {"$set": {"uid": user_id}}, upsert=True)

async def remove_dragon(user_id: int):
    await dragons_col.delete_one({"uid": user_id})

async def is_dragon(user_id: int) -> bool:
    return bool(await dragons_col.find_one({"uid": user_id}))

async def get_dragons() -> list:
    return [d["uid"] async for d in dragons_col.find({})]


# ── DEMONS (SUPPORT) ────────────────────────────────────────────
async def add_demon(user_id: int):
    await demons_col.update_one({"uid": user_id}, {"$set": {"uid": user_id}}, upsert=True)

async def remove_demon(user_id: int):
    await demons_col.delete_one({"uid": user_id})

async def is_demon(user_id: int) -> bool:
    return bool(await demons_col.find_one({"uid": user_id}))

async def get_demons() -> list:
    return [d["uid"] async for d in demons_col.find({})]


# ── TIGERS ──────────────────────────────────────────────────────
async def add_tiger(user_id: int):
    await tigers_col.update_one({"uid": user_id}, {"$set": {"uid": user_id}}, upsert=True)

async def remove_tiger(user_id: int):
    await tigers_col.delete_one({"uid": user_id})

async def is_tiger(user_id: int) -> bool:
    return bool(await tigers_col.find_one({"uid": user_id}))

async def get_tigers() -> list:
    return [d["uid"] async for d in tigers_col.find({})]


# ── WOLVES (WHITELIST) ──────────────────────────────────────────
async def add_wolf(user_id: int):
    await wolves_col.update_one({"uid": user_id}, {"$set": {"uid": user_id}}, upsert=True)

async def remove_wolf(user_id: int):
    await wolves_col.delete_one({"uid": user_id})

async def is_wolf(user_id: int) -> bool:
    return bool(await wolves_col.find_one({"uid": user_id}))

async def get_wolves() -> list:
    return [d["uid"] async for d in wolves_col.find({})]
