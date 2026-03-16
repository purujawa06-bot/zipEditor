import os
import time
from pathlib import Path
from config import BASE_DIR

# State sesi disimpan di memory server
SESSIONS: dict = {}


def get_session_dir(session_id: str) -> Path:
    return BASE_DIR / session_id


def update_session_activity(session_id: str):
    if session_id in SESSIONS:
        SESSIONS[session_id]["last_active"] = time.time()

    session_dir = get_session_dir(session_id)
    if session_dir.exists():
        os.utime(session_dir, None)


async def broadcast_ws(session_id: str, message: dict):
    if session_id in SESSIONS and SESSIONS[session_id].get("ws"):
        try:
            await SESSIONS[session_id]["ws"].send_json(message)
        except Exception:
            pass


async def send_vfs_update(session_id: str):
    from vfs import get_vfs_list  # lazy import to avoid circular
    await broadcast_ws(session_id, {"type": "vfs", "data": get_vfs_list(session_id)})
