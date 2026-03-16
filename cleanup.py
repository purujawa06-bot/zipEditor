import asyncio
import shutil
import time
from config import BASE_DIR, SESSION_TIMEOUT
from session import SESSIONS, get_session_dir


async def cleanup_old_sessions():
    """Background task: hapus sesi yang sudah tidak aktif melebihi SESSION_TIMEOUT."""
    while True:
        now = time.time()
        to_delete = []

        for sid, data in SESSIONS.items():
            if now - data["last_active"] > SESSION_TIMEOUT:
                to_delete.append(sid)

        for sid in to_delete:
            del SESSIONS[sid]
            sid_dir = get_session_dir(sid)
            if sid_dir.exists():
                shutil.rmtree(sid_dir)

        # Bersihkan folder di disk yang tidak ada di memory
        if BASE_DIR.exists():
            for folder in BASE_DIR.iterdir():
                if folder.is_dir() and folder.name not in SESSIONS:
                    if now - folder.stat().st_mtime > SESSION_TIMEOUT:
                        shutil.rmtree(folder)

        await asyncio.sleep(600)
