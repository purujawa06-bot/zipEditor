import os
from pathlib import Path
from session import get_session_dir


def get_vfs_list(session_id: str) -> list:
    session_dir = get_session_dir(session_id)
    if not session_dir.exists():
        return []
    files = []
    for root, _, filenames in os.walk(session_dir):
        for filename in filenames:
            full_path = Path(root) / filename
            rel_path = full_path.relative_to(session_dir).as_posix()
            files.append(rel_path)
    return sorted(files)


def is_binary(file_path: Path) -> bool:
    try:
        with open(file_path, 'tr') as check_file:
            check_file.read(1024)
            return False
    except UnicodeDecodeError:
        return True
