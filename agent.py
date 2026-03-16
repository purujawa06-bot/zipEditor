import asyncio
import httpx
from config import API_URL, BASE_DELAY, SYSTEM_PROMPT, SYSTEM_PROMPT_TODO
from session import SESSIONS, update_session_activity, broadcast_ws, send_vfs_update
from vfs import get_vfs_list
from executor import execute_command


# ==========================================
# FETCH AI
# ==========================================
async def fetch_ai(prompt_text: str) -> str:
    async with httpx.AsyncClient(timeout=90.0) as client:
        response = await client.post(API_URL, json={"prompt": prompt_text})
        response.raise_for_status()
        data = response.json()
        return data['result']['answer']


# ==========================================
# TODO PLANNER (dipanggil otomatis sebelum loop)
# ==========================================
async def run_todo_planner(session_id: str, initial_prompt: str, vfs_context: str):
    """Memanggil AI Todo untuk membuat rencana singkat sebelum loop eksekusi dimulai."""
    session = SESSIONS[session_id]

    await broadcast_ws(session_id, {"type": "status", "text": "Membuat rencana Todo...", "statusType": "active"})

    todo_payload = (
        f"{SYSTEM_PROMPT_TODO}\n\n"
        f"[Struktur File Saat Ini: {vfs_context}]\n\n"
        f"Instruksi User: {initial_prompt}\n\n"
        f"PuruAI-Todo, buat rencana singkat:"
    )

    todo_response = await fetch_ai(todo_payload)

    todo_sys_msg = f"SystemLog (Todo Plan):\n{todo_response}"
    session["chat_history"].append({"role": "system", "text": todo_sys_msg})
    session["ai_memory"].append({"role": "system", "text": todo_sys_msg})
    await broadcast_ws(session_id, {"type": "chat_update", "data": session["chat_history"]})


# ==========================================
# AGENT LOOP UTAMA
# ==========================================
async def agent_loop(session_id: str, initial_prompt: str):
    session = SESSIONS[session_id]
    session["is_looping"] = True
    error_count = 0

    # Tambahkan pesan user ke history
    session["chat_history"].append({"role": "user", "text": initial_prompt})
    session["ai_memory"].append({"role": "user", "text": initial_prompt})
    await broadcast_ws(session_id, {"type": "chat_update", "data": session["chat_history"]})
    await broadcast_ws(session_id, {"type": "status", "text": "Berpikir...", "statusType": "active"})

    # Ambil konteks VFS awal
    vfs_list = get_vfs_list(session_id)
    vfs_context = 'Kosong' if not vfs_list else ', '.join(vfs_list)

    # ── Panggil Todo Planner sebelum loop ──────────────────────────────
    try:
        await run_todo_planner(session_id, initial_prompt, vfs_context)
    except Exception as e:
        todo_err = f"SystemLog (Todo Error): Gagal membuat rencana - {str(e)}"
        session["chat_history"].append({"role": "system", "text": todo_err})
        session["ai_memory"].append({"role": "system", "text": todo_err})
        await broadcast_ws(session_id, {"type": "chat_update", "data": session["chat_history"]})

    # ── Loop Eksekusi Utama ────────────────────────────────────────────
    while session["is_looping"]:
        try:
            update_session_activity(session_id)

            vfs_list = get_vfs_list(session_id)
            vfs_context = 'Kosong' if not vfs_list else ', '.join(vfs_list)

            base_payload = f"{SYSTEM_PROMPT}\n\n[Context VFS Saat Ini: {vfs_context}]\n\n"
            history_log = "\n".join([f"{m['role'].upper()}: {m['text']}" for m in session["ai_memory"]])
            full_prompt = f"{base_payload}Riwayat:\n{history_log}\n\nPuruAI, berikan tindakan Anda selanjutnya!"

            await broadcast_ws(session_id, {"type": "status", "text": "Berpikir...", "statusType": "active"})
            ai_response = await fetch_ai(full_prompt)

            session["chat_history"].append({"role": "ai", "text": ai_response})
            session["ai_memory"].append({"role": "ai", "text": ai_response})
            await broadcast_ws(session_id, {"type": "chat_update", "data": session["chat_history"]})

            exec_result = execute_command(session_id, ai_response)

            if exec_result:
                await send_vfs_update(session_id)

                if exec_result["action"] == "stop":
                    msg = "Agent selesai. Semua ingatan AI telah dihapus (File VFS & Media tetap aman). Anda dapat mendownload atau memberi instruksi baru."
                    session["chat_history"].append({"role": "system", "text": msg})
                    session["ai_memory"] = []

                    await broadcast_ws(session_id, {"type": "chat_update", "data": session["chat_history"]})
                    await broadcast_ws(session_id, {"type": "status", "text": "Selesai", "statusType": "done", "isLooping": False})
                    session["is_looping"] = False
                    break

                elif exec_result["action"] == "todo":
                    # Trigger ulang Todo Planner untuk re-planning
                    sys_msg = "SystemLog (Re-Planning): AI meminta pembaruan rencana Todo..."
                    session["chat_history"].append({"role": "system", "text": sys_msg})
                    session["ai_memory"].append({"role": "system", "text": sys_msg})
                    await broadcast_ws(session_id, {"type": "chat_update", "data": session["chat_history"]})
                    try:
                        await run_todo_planner(session_id, initial_prompt, vfs_context)
                    except Exception as e:
                        todo_err = f"SystemLog (Todo Error): Gagal membuat rencana baru - {str(e)}"
                        session["chat_history"].append({"role": "system", "text": todo_err})
                        session["ai_memory"].append({"role": "system", "text": todo_err})
                        await broadcast_ws(session_id, {"type": "chat_update", "data": session["chat_history"]})

                else:
                    sys_msg = f"SystemLog ({exec_result['action']}): {exec_result['log']}"
                    session["chat_history"].append({"role": "system", "text": sys_msg})
                    session["ai_memory"].append({"role": "system", "text": sys_msg})
                    await broadcast_ws(session_id, {"type": "chat_update", "data": session["chat_history"]})
                    error_count = 0

            else:
                sys_msg = "SystemLog (Warning): Tidak ada tag <execution> valid ditemukan."
                session["chat_history"].append({"role": "system", "text": sys_msg})
                session["ai_memory"].append({"role": "system", "text": sys_msg})
                await broadcast_ws(session_id, {"type": "chat_update", "data": session["chat_history"]})

            await broadcast_ws(session_id, {"type": "status", "text": f"Jeda {BASE_DELAY}s...", "statusType": "idle"})
            await asyncio.sleep(BASE_DELAY)

        except Exception as e:
            error_count += 1
            backoff = BASE_DELAY * (2 ** error_count)
            err_msg = f"SystemLog (API Error): {str(e)}. Retry dalam {backoff}s (Ke-{error_count})"

            session["chat_history"].append({"role": "system", "text": err_msg})
            session["ai_memory"].append({"role": "system", "text": err_msg})
            await broadcast_ws(session_id, {"type": "chat_update", "data": session["chat_history"]})
            await broadcast_ws(session_id, {"type": "status", "text": f"Error. Wait {backoff}s", "statusType": "error"})

            await asyncio.sleep(backoff)

            if error_count > 4:
                stop_msg = "Terlalu banyak error. Loop dihentikan paksa."
                session["chat_history"].append({"role": "system", "text": stop_msg})
                await broadcast_ws(session_id, {"type": "chat_update", "data": session["chat_history"]})
                await broadcast_ws(session_id, {"type": "status", "text": "Terhenti", "statusType": "idle", "isLooping": False})
                session["is_looping"] = False
                break
