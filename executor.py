import os
import re
import shutil
import subprocess
from pathlib import Path
from typing import Optional
from session import get_session_dir
from vfs import get_vfs_list, is_binary


def execute_command(session_id: str, command_str: str) -> Optional[dict]:
    session_dir = get_session_dir(session_id)
    os.makedirs(session_dir, exist_ok=True)

    try:
        exec_match = re.search(r'<execution>([\s\S]*?)</execution>', command_str, re.IGNORECASE)
        if not exec_match:
            return None

        cmd_body = exec_match.group(1).strip()

        # ── stop ──────────────────────────────────────────────────────────
        if cmd_body == 'stop':
            return {"action": "stop", "log": "Berhasil dihentikan. Siap untuk diunduh."}

        # ── todo (trigger ulang Todo Planner) ─────────────────────────────
        if cmd_body == 'todo':
            return {"action": "todo", "log": "AI meminta pembuatan ulang rencana Todo."}

        # ── all ───────────────────────────────────────────────────────────
        if cmd_body.startswith('all'):
            files = get_vfs_list(session_id)
            log = "Project kosong." if not files else "Daftar file:\n" + "\n".join(files)
            return {"action": "all", "log": f"Berhasil membaca struktur.\n{log}"}

        # ── read ──────────────────────────────────────────────────────────
        if cmd_body.startswith('read'):
            path_match = re.search(r'<path>(.*?)</path>', cmd_body, re.IGNORECASE)
            if not path_match:
                raise Exception("Tag <path> tidak ditemukan.")

            clean_path = path_match.group(1).replace('#root/', '').strip()
            file_path = session_dir / clean_path

            if file_path.exists() and file_path.is_file():
                if is_binary(file_path):
                    return {"action": "read", "log": f"Isi dari {clean_path}:\n[File Binary/Media tidak dapat dibaca sebagai teks]"}
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                return {"action": "read", "log": f"Isi dari {clean_path}:\n{content}"}
            else:
                raise Exception(f"File {clean_path} tidak ditemukan.")

        # ── write ─────────────────────────────────────────────────────────
        if cmd_body.startswith('write'):
            path_match = re.search(r'<path>(.*?)</path>', cmd_body, re.IGNORECASE)
            content_match = re.search(r'<content>([\s\S]*?)</content>', cmd_body, re.IGNORECASE)
            if not path_match or not content_match:
                raise Exception("Tag <path> atau <content> tidak lengkap.")

            clean_path = path_match.group(1).replace('#root/', '').strip()
            content = content_match.group(1)
            file_path = session_dir / clean_path

            os.makedirs(file_path.parent, exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return {"action": "write", "log": f"Berhasil menulis ke file {clean_path}."}

        # ── remove ────────────────────────────────────────────────────────
        if cmd_body.startswith('remove'):
            path_match = re.search(r'<path>(.*?)</path>', cmd_body, re.IGNORECASE)
            if not path_match:
                raise Exception("Tag <path> tidak ditemukan.")

            clean_path = path_match.group(1).replace('#root/', '').strip()
            file_path = session_dir / clean_path

            if file_path.exists():
                os.remove(file_path)
                return {"action": "remove", "log": f"File {clean_path} berhasil dihapus."}
            else:
                raise Exception(f"File {clean_path} tidak ditemukan.")

        # ── move ──────────────────────────────────────────────────────────
        if cmd_body.startswith('move'):
            path_match = re.search(r'<path>(.*?)</path>', cmd_body, re.IGNORECASE)
            to_match = re.search(r'<to>(.*?)</to>', cmd_body, re.IGNORECASE)
            if not path_match or not to_match:
                raise Exception("Tag <path> atau <to> tidak ditemukan.")

            src_clean = path_match.group(1).replace('#root/', '').strip()
            dst_clean = to_match.group(1).replace('#root/', '').strip()
            src_path = session_dir / src_clean
            dst_path = session_dir / dst_clean

            if src_path.exists():
                os.makedirs(dst_path.parent, exist_ok=True)
                shutil.move(str(src_path), str(dst_path))
                return {"action": "move", "log": f"Berhasil memindahkan/rename: {src_clean} -> {dst_clean}"}
            else:
                raise Exception(f"File sumber {src_clean} tidak ditemukan.")

        # ── curl ──────────────────────────────────────────────────────────
        if cmd_body.startswith('curl'):
            content_match = re.search(r'<content>([\s\S]*?)</content>', cmd_body, re.IGNORECASE)
            if not content_match:
                raise Exception("Tag <content> tidak ditemukan untuk perintah curl.")

            curl_command = content_match.group(1).strip()
            if not curl_command.startswith('curl '):
                raise Exception("Hanya perintah curl yang diperbolehkan.")

            result = subprocess.run(
                curl_command,
                shell=True,
                cwd=str(session_dir),
                capture_output=True,
                text=True,
                timeout=45
            )
            output = result.stdout if result.returncode == 0 else f"Error Output:\n{result.stderr}"
            if len(output) > 2000:
                output = output[:2000] + "... [Terpotong karena terlalu panjang]"
            return {"action": "curl", "log": f"Eksekusi selesai dengan kode {result.returncode}.\nOutput:\n{output}"}

        raise Exception("Perintah tidak dikenali.")

    except Exception as e:
        return {"action": "error", "log": f"ERROR: {str(e)}"}
