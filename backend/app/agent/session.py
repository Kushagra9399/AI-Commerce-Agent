from typing import Dict, List


_sessions: Dict[str, List[dict]] = {}


def get_session(session_id: str) -> List[dict]:
    if session_id not in _sessions:
        _sessions[session_id] = []

    return _sessions[session_id]


def clear_session(session_id: str):
    _sessions.pop(session_id, None)