"""
Active file state management for markdown-vault.

This module provides session-based tracking of the currently active file,
allowing clients to maintain context across multiple API requests without
repeatedly specifying the file path.
"""

import logging
import threading
from typing import Dict

logger = logging.getLogger(__name__)


class ActiveFileManager:
    """
    Manages active file state per session.

    Provides thread-safe in-memory storage of the currently active file
    for each client session, enabling stateful operations.
    """

    def __init__(self) -> None:
        """
        Initialize the active file manager.

        Creates an empty session store and thread lock for synchronization.
        """
        self._sessions: Dict[str, str] = {}
        self._lock = threading.Lock()
        logger.info("Initialized ActiveFileManager")

    def get_active_file(self, session_id: str) -> str | None:
        """
        Get the active file path for a session.

        Args:
            session_id: Unique session identifier

        Returns:
            Active file path relative to vault root, or None if not set
        """
        with self._lock:
            filepath = self._sessions.get(session_id)
            logger.debug(f"Get active file for session {session_id}: {filepath}")
            return filepath

    def set_active_file(self, session_id: str, filepath: str) -> None:
        """
        Set the active file path for a session.

        Args:
            session_id: Unique session identifier
            filepath: File path relative to vault root
        """
        with self._lock:
            self._sessions[session_id] = filepath
            logger.info(f"Set active file for session {session_id}: {filepath}")

    def clear_active_file(self, session_id: str) -> None:
        """
        Clear the active file for a session.

        Args:
            session_id: Unique session identifier
        """
        with self._lock:
            if session_id in self._sessions:
                filepath = self._sessions.pop(session_id)
                logger.info(f"Cleared active file for session {session_id}: {filepath}")
            else:
                logger.debug(f"No active file to clear for session {session_id}")

    def clear_all(self) -> None:
        """
        Clear all active files for all sessions.

        Useful for cleanup or testing purposes.
        """
        with self._lock:
            count = len(self._sessions)
            self._sessions.clear()
            logger.info(f"Cleared all active files ({count} sessions)")


__all__ = ["ActiveFileManager"]
