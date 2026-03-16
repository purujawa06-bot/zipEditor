import asyncio
import json
import os
import shutil
import time
import zipfile

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, UploadFile, File, Form
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse

from session import SESSIONS, get_session_dir, update_session_activity, send_vfs_update, broadcast_ws
from vfs import get_vfs_list
from agent import agent_loop
from frontend import HTML_CONTENT

router = APIRouter()


@router.get("/")
async def get_ui():
    return HTMLResponse(HTML_CONTENT)


@router.get("/api/check_session/{session_id}")
async def check_session(session_id: str):
    session_dir = get_session_dir(session_id)
    if session_id in SESSIONS or session_dir.exists():
        return {"valid": True}
    return {"valid": False}


@router.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await websocket.accept()

    if session_id not in SESSIONS:
        SESSIONS[session_id] = {
            "chat_history": [],
            "ai_memory": [],
            "is_looping": False,
            "last_active": time.time(),
            "ws": websocket
        }
    else:
        SESSIONS[session_id]["ws"] = websocket
        update_session_activity(session_id)

    session = SESSIONS[session_id]

    await websocket.send_json({"type": "chat_update", "data": session["chat_history"]})
    await websocket.send_json({"type": "vfs", "data": get_vfs_list(session_id)})
    await websocket.send_json({"type": "loop_state", "isLooping": session["is_looping"]})
    if session["is_looping"]:
        await websocket.send_json({"type": "status", "text": "Melanjutkan...", "statusType": "active"})

    try:
        while True:
            data = await websocket.receive_text()
            payload = json.loads(data)

            if payload["action"] == "prompt" and not session["is_looping"]:
                prompt_text = payload["text"]
                asyncio.create_task(agent_loop(session_id, prompt_text))

    except WebSocketDisconnect:
        if session_id in SESSIONS:
            SESSIONS[session_id]["ws"] = None


@router.post("/api/upload_zip")
async def upload_zip(session_id: str = Form(...), file: UploadFile = File(...)):
    session_dir = get_session_dir(session_id)
    if session_dir.exists():
        shutil.rmtree(session_dir)
    os.makedirs(session_dir, exist_ok=True)

    temp_zip = session_dir / "temp.zip"
    with open(temp_zip, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        with zipfile.ZipFile(temp_zip, 'r') as zip_ref:
            zip_ref.extractall(session_dir)
        os.remove(temp_zip)

        if session_id in SESSIONS:
            SESSIONS[session_id]["chat_history"] = []
            SESSIONS[session_id]["ai_memory"] = []
            SESSIONS[session_id]["chat_history"].append(
                {"role": "system", "text": f"Berhasil memuat ZIP: {file.filename}."}
            )
            await send_vfs_update(session_id)
            await broadcast_ws(session_id, {"type": "chat_update", "data": SESSIONS[session_id]["chat_history"]})

        return {"status": "success"}
    except Exception as e:
        return JSONResponse(status_code=400, content={"error": str(e)})


@router.post("/api/upload_context")
async def upload_context(session_id: str = Form(...), file: UploadFile = File(...)):
    """Upload referensi file / media melalui chat (masuk ke _context_upload)"""
    session_dir = get_session_dir(session_id)
    context_dir = session_dir / "_context_upload"
    os.makedirs(context_dir, exist_ok=True)

    file_path = context_dir / file.filename
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    if session_id in SESSIONS:
        msg = f"User telah mengunggah file konteks: #root/_context_upload/{file.filename}"
        SESSIONS[session_id]["chat_history"].append({"role": "system", "text": msg})
        SESSIONS[session_id]["ai_memory"].append({"role": "system", "text": msg})

        await send_vfs_update(session_id)
        await broadcast_ws(session_id, {"type": "chat_update", "data": SESSIONS[session_id]["chat_history"]})

    return {"status": "success", "filename": file.filename}


@router.get("/api/download_zip/{session_id}")
async def download_zip(session_id: str):
    session_dir = get_session_dir(session_id)
    if not session_dir.exists():
        return JSONResponse(status_code=404, content={"error": "Session/Data tidak ditemukan"})

    zip_filename = f"/tmp/PuruAI_Project_{session_id}.zip"

    if os.path.exists(zip_filename):
        os.remove(zip_filename)

    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(session_dir):
            # Abaikan folder _context_upload pada proses Download
            if "_context_upload" in root.split(os.sep):
                continue
            for f in files:
                file_path = os.path.join(root, f)
                arcname = os.path.relpath(file_path, session_dir)
                zipf.write(file_path, arcname)

    return FileResponse(zip_filename, media_type="application/zip", filename=f"PuruAI_Project_{int(time.time())}.zip")


@router.post("/api/clear_session")
async def clear_session(session_id: str = Form(...)):
    if session_id in SESSIONS:
        SESSIONS[session_id]["chat_history"] = [
            {"role": "system", "text": "Sistem dikosongkan. File project Anda tetap aman."}
        ]
        SESSIONS[session_id]["ai_memory"] = []
        SESSIONS[session_id]["is_looping"] = False

    await send_vfs_update(session_id)
    await broadcast_ws(session_id, {"type": "chat_update", "data": SESSIONS[session_id]["chat_history"]})
    return {"status": "success"}


@router.post("/api/delete_session")
async def delete_session(session_id: str = Form(...)):
    if session_id in SESSIONS:
        del SESSIONS[session_id]

    session_dir = get_session_dir(session_id)
    if session_dir.exists():
        shutil.rmtree(session_dir)

    return {"status": "success"}
