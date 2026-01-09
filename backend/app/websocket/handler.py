"""
WebSocket Handler for Real-Time Updates

This module manages WebSocket connections and broadcasts real-time
updates from the capacity planning workflow to connected clients.

FEATURES:
- Connection management (connect/disconnect)
- Session-based messaging
- Broadcast to all clients
- JSON serialization with Pydantic models
"""
import asyncio
import json
from typing import Dict, Set, Any, Optional
from datetime import datetime
from fastapi import WebSocket, WebSocketDisconnect
from pydantic import BaseModel


class WebSocketManager:
    """
    Manages WebSocket connections for real-time workflow updates.

    This class handles:
    - Client connection lifecycle
    - Session-based routing
    - Message broadcasting
    - JSON serialization
    """

    def __init__(self):
        # Active connections per session
        self._connections: Dict[str, Set[WebSocket]] = {}
        # All active connections
        self._all_connections: Set[WebSocket] = set()
        # Lock for thread-safe operations
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket, session_id: Optional[str] = None):
        """
        Accept a new WebSocket connection.

        Args:
            websocket: The WebSocket connection
            session_id: Optional session ID to associate with this connection
        """
        await websocket.accept()

        async with self._lock:
            self._all_connections.add(websocket)

            if session_id:
                if session_id not in self._connections:
                    self._connections[session_id] = set()
                self._connections[session_id].add(websocket)

    async def disconnect(self, websocket: WebSocket, session_id: Optional[str] = None):
        """
        Remove a WebSocket connection.

        Args:
            websocket: The WebSocket connection to remove
            session_id: Optional session ID associated with this connection
        """
        async with self._lock:
            self._all_connections.discard(websocket)

            if session_id and session_id in self._connections:
                self._connections[session_id].discard(websocket)
                if not self._connections[session_id]:
                    del self._connections[session_id]

    async def send_to_session(self, session_id: str, message: Any):
        """
        Send a message to all connections in a session.

        Args:
            session_id: The session to send to
            message: The message to send (will be JSON serialized)
        """
        async with self._lock:
            connections = self._connections.get(session_id, set()).copy()

        await self._send_to_connections(connections, message)

    async def broadcast(self, message: Any):
        """
        Broadcast a message to all connected clients.

        Args:
            message: The message to send (will be JSON serialized)
        """
        async with self._lock:
            connections = self._all_connections.copy()

        await self._send_to_connections(connections, message)

    async def _send_to_connections(self, connections: Set[WebSocket], message: Any):
        """Send a message to a set of connections."""
        if not connections:
            return

        # Serialize the message
        json_message = self._serialize(message)

        # Send to all connections, removing disconnected ones
        disconnected = []
        for connection in connections:
            try:
                await connection.send_text(json_message)
            except Exception:
                disconnected.append(connection)

        # Clean up disconnected clients
        for conn in disconnected:
            await self.disconnect(conn)

    def _serialize(self, message: Any) -> str:
        """Serialize a message to JSON."""
        if isinstance(message, BaseModel):
            return message.model_dump_json()
        elif isinstance(message, dict):
            return json.dumps(message, default=self._json_serializer)
        else:
            return json.dumps({"data": str(message)})

    def _json_serializer(self, obj):
        """Custom JSON serializer for non-standard types."""
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, BaseModel):
            return obj.model_dump()
        return str(obj)

    @property
    def active_sessions(self) -> int:
        """Get the number of active sessions."""
        return len(self._connections)

    @property
    def total_connections(self) -> int:
        """Get the total number of active connections."""
        return len(self._all_connections)


# Global WebSocket manager instance
ws_manager = WebSocketManager()


async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """
    WebSocket endpoint handler for workflow updates.

    This function handles the WebSocket lifecycle:
    1. Accept connection
    2. Listen for messages (e.g., approval responses)
    3. Handle disconnection

    Args:
        websocket: The WebSocket connection
        session_id: The workflow session ID
    """
    await ws_manager.connect(websocket, session_id)

    try:
        while True:
            # Wait for messages from the client
            data = await websocket.receive_text()

            # Parse the message
            try:
                message = json.loads(data)
                message_type = message.get("type")

                if message_type == "ping":
                    # Respond to ping with pong
                    await websocket.send_text(json.dumps({"type": "pong"}))

                elif message_type == "approval":
                    # Handle approval response - this would trigger workflow continuation
                    # The workflow.approve() method should be called from the API endpoint
                    pass

            except json.JSONDecodeError:
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": "Invalid JSON"
                }))

    except WebSocketDisconnect:
        await ws_manager.disconnect(websocket, session_id)
