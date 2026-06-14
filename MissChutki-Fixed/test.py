import re

path = "Emilia/__main__.py"
with open(path, "r") as f:
    src = f.read()

# 1. Replace stop_telethon_sync to use asyncio.run() instead of run_coroutine_threadsafe
old_sync = '''def stop_telethon_sync():
    try:
        if not telethn:
            return
        connected = False
        try:
            connected = telethn.is_connected()
        except Exception:
            connected = True
        if not connected:
            return
        LOGGER.info("Stopping Telethon client...")
        loop = getattr(telethn, "_loop", None) or asyncio.get_event_loop()
        fut = asyncio.run_coroutine_threadsafe(telethn.disconnect(), loop)
        try:
            fut.result(timeout=5)
        except Exception as e:
            LOGGER.error(f"Error during Telethon shutdown: {e}")
        else:
            LOGGER.info("Telethon client stopped.")
    except Exception as e:
        LOGGER.error(f"Error stopping Telethon client: {e}")'''

new_sync = '''def stop_telethon_sync():
    """Disconnect Telethon using a fresh event loop (called after main loop has exited)."""
    try:
        if not telethn:
            return
        try:
            if not telethn.is_connected():
                LOGGER.info("Telethon client already disconnected, skipping.")
                return
        except Exception:
            pass  # if we can\'t check, attempt disconnect anyway
        LOGGER.info("Stopping Telethon client...")
        asyncio.run(telethn.disconnect())
        LOGGER.info("Telethon client stopped.")
    except Exception as e:
        LOGGER.error(f"Error stopping Telethon client: {e}")'''

if old_sync in src:
    src = src.replace(old_sync, new_sync)
    print("✅ Replaced stop_telethon_sync")
else:
    print("❌ Could not find stop_telethon_sync to replace — check manually")

with open(path, "w") as f:
    f.write(src)

print("Done.")
