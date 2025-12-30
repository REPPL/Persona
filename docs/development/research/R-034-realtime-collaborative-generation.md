# R-034: Real-Time Collaborative Generation

## Executive Summary

This research analyses approaches for enabling multiple users to generate and refine personas simultaneously. Real-time collaboration enables team workshops, live research sessions, and distributed persona development. Recommended approach: WebSocket-based collaboration with operational transformation for conflict resolution.

---

## Research Context

| Attribute | Value |
|-----------|-------|
| **ID** | R-034 |
| **Category** | Team Features |
| **Status** | Complete |
| **Priority** | P3 |
| **Informs** | v2.0.0 collaboration features |

---

## Problem Statement

Team-based persona development requires:
- Multiple users working on the same persona simultaneously
- Real-time visibility into others' changes
- Conflict resolution for concurrent edits
- Session management for workshops
- Live generation streaming

Currently, Persona is single-user and requires file-based sharing.

---

## State of the Art Analysis

### Collaboration Models

| Model | Latency | Complexity | Use Case |
|-------|---------|------------|----------|
| **File sharing** | High | Low | Async work |
| **Polling** | Medium | Low | Near-real-time |
| **WebSocket** | Low | Medium | Real-time |
| **WebRTC** | Very low | High | P2P collaboration |
| **CRDT** | Low | High | Offline-first |

### Real-Time Architectures

**WebSocket Server:**
```python
from fastapi import FastAPI, WebSocket
from typing import Dict, Set

app = FastAPI()
connections: Dict[str, Set[WebSocket]] = {}

@app.websocket("/ws/session/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await websocket.accept()

    if session_id not in connections:
        connections[session_id] = set()
    connections[session_id].add(websocket)

    try:
        while True:
            data = await websocket.receive_json()
            # Broadcast to all participants
            for ws in connections[session_id]:
                if ws != websocket:
                    await ws.send_json(data)
    finally:
        connections[session_id].discard(websocket)
```

**Operational Transformation:**
```python
@dataclass
class Operation:
    type: str  # "insert", "delete", "update"
    path: str  # JSON path
    value: Any
    timestamp: int
    user_id: str

class OTEngine:
    def transform(self, op1: Operation, op2: Operation) -> Operation:
        """Transform op1 against op2 for concurrent application."""
        if op1.path == op2.path:
            if op1.timestamp < op2.timestamp:
                return op1  # Earlier wins
            else:
                # Transform based on operation type
                return self._transform_same_path(op1, op2)
        return op1  # No conflict
```

**CRDT (Conflict-free Replicated Data Types):**
```python
from crdt import LWWRegister, ORSet

class CollaborativePersona:
    def __init__(self):
        self.name = LWWRegister()
        self.demographics = {}
        self.goals = ORSet()  # Add-wins set

    def set_name(self, value: str, timestamp: int) -> None:
        self.name.set(value, timestamp)

    def add_goal(self, goal: str) -> None:
        self.goals.add(goal)
```

### Streaming Generation

```python
async def stream_generation(
    websocket: WebSocket,
    data: str,
    session_id: str
) -> None:
    async for chunk in provider.stream_generate(data):
        # Broadcast chunk to all participants
        for ws in connections[session_id]:
            await ws.send_json({
                "type": "generation_chunk",
                "content": chunk,
                "timestamp": time.time()
            })
```

### Session Management

```python
@dataclass
class CollaborationSession:
    id: str
    name: str
    created_by: str
    created_at: datetime
    participants: list[str]
    persona_id: str
    state: dict  # Current persona state
    history: list[Operation]

class SessionManager:
    async def create_session(
        self,
        name: str,
        creator: str,
        persona_id: str | None = None
    ) -> CollaborationSession:
        session = CollaborationSession(
            id=str(uuid4()),
            name=name,
            created_by=creator,
            created_at=datetime.now(),
            participants=[creator],
            persona_id=persona_id or str(uuid4()),
            state={},
            history=[]
        )
        await self._store(session)
        return session

    async def join_session(
        self,
        session_id: str,
        user_id: str
    ) -> CollaborationSession:
        session = await self._load(session_id)
        session.participants.append(user_id)
        await self._store(session)
        return session
```

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│              Real-Time Collaboration Architecture            │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Clients                                                     │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐                     │
│  │ User A  │  │ User B  │  │ User C  │                     │
│  └────┬────┘  └────┬────┘  └────┬────┘                     │
│       │            │            │                           │
│       └────────────┼────────────┘                           │
│                    │ WebSocket                              │
│                    ▼                                        │
│         ┌───────────────────┐                              │
│         │ Collaboration Hub │                              │
│         │  ┌─────────────┐  │                              │
│         │  │  Sessions   │  │                              │
│         │  │  Manager    │  │                              │
│         │  └─────────────┘  │                              │
│         │  ┌─────────────┐  │                              │
│         │  │    OT/CRDT  │  │                              │
│         │  │   Engine    │  │                              │
│         │  └─────────────┘  │                              │
│         └───────────────────┘                              │
│                    │                                        │
│                    ▼                                        │
│         ┌───────────────────┐                              │
│         │   State Store     │                              │
│         │   (Redis/DB)      │                              │
│         └───────────────────┘                              │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Evaluation Matrix

| Feature | WebSocket + OT | CRDT | WebRTC |
|---------|----------------|------|--------|
| Latency | Low | Low | Very low |
| Offline support | ❌ | ✅ | ❌ |
| Server requirements | Medium | Low | Low |
| Complexity | Medium | High | High |
| Scalability | ✅ | ✅ | ⚠️ |

---

## Recommended Approach

### Phase 1: Basic Collaboration
- WebSocket server for real-time updates
- Simple last-write-wins conflict resolution
- Session creation and joining

### Phase 2: Advanced Conflict Resolution
- Operational transformation for concurrent edits
- Edit history and undo support
- User presence indicators

### Phase 3: Workshop Mode
- Live generation streaming
- Turn-based editing
- Voting and consensus features

### CLI/API Interface

```bash
# Create collaboration session
persona session create "Workshop 2025-01-15" --share

# Join session
persona session join abc123

# List active sessions
persona session list

# Start collaborative generation
persona generate --session abc123 --from data/
```

**WebSocket Events:**
```json
// User joins
{"type": "user_joined", "user_id": "alice", "timestamp": 1705312800}

// Edit operation
{"type": "edit", "path": "demographics.age", "value": 34, "user_id": "bob"}

// Generation started
{"type": "generation_started", "user_id": "alice"}

// Generation chunk
{"type": "generation_chunk", "content": "Sarah is a...", "index": 0}

// Generation complete
{"type": "generation_complete", "persona": {...}}
```

### Configuration

```yaml
collaboration:
  enabled: false  # Feature flag

  server:
    host: 0.0.0.0
    port: 8080
    max_sessions: 100
    max_participants_per_session: 10

  conflict_resolution: last_write_wins  # last_write_wins, ot, crdt

  session:
    timeout_minutes: 60
    persist_history: true

  streaming:
    enabled: true
    chunk_size: 50
```

---

## Security Considerations

- Session access control
- User authentication
- Rate limiting
- Input validation
- Audit logging

---

## References

1. [Operational Transformation](https://operational-transformation.github.io/)
2. [CRDTs](https://crdt.tech/)
3. [WebSocket Protocol](https://tools.ietf.org/html/rfc6455)
4. [Yjs](https://yjs.dev/) - CRDT implementation
5. [Socket.IO](https://socket.io/)

---

## Related Documentation

- [R-021: Multi-User & Team Collaboration](R-021-multi-user-collaboration.md)
- [F-105: REST API](../roadmap/features/completed/F-105-rest-api.md)
- [ADR-0036: Multi-Tenancy Architecture](../decisions/adrs/ADR-0036-multi-tenancy-architecture.md)

---

**Status**: Complete
