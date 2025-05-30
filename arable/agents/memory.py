"""
Agent Memory System for ARABLE
Provides persistent state management and inter-agent communication
"""

import json
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
import logging
from dataclasses import dataclass, field
from abc import ABC, abstractmethod

@dataclass
class MemoryEntry:
    """Individual memory entry with metadata"""
    key: str
    value: Any
    agent_id: str
    timestamp: datetime
    memory_type: str = "general"  # general, task_result, workflow_state, etc.
    ttl: Optional[int] = None  # Time to live in seconds
    tags: List[str] = field(default_factory=list)  # <-- default empty list

class MemoryBackend(ABC):
    """Abstract base for memory storage backends"""
    @abstractmethod
    async def store(self, entry: MemoryEntry) -> bool:
        pass
    @abstractmethod
    async def retrieve(self, key: str, agent_id: Optional[str] = None) -> Optional[MemoryEntry]:
        pass
    @abstractmethod
    async def search(self, query: Dict[str, Any]) -> List[MemoryEntry]:
        pass
    @abstractmethod
    async def delete(self, key: str, agent_id: Optional[str] = None) -> bool:
        pass

class FileMemoryBackend(MemoryBackend):
    """File-based memory backend using JSON storage"""

    def __init__(self, storage_path: Path = None):
        self.storage_path = storage_path or Path("./memory_store")
        self.storage_path.mkdir(exist_ok=True)
        self.logger = logging.getLogger("arable.agents.memory.file")

    def _get_agent_file(self, agent_id: str) -> Path:
        """Get storage file path for agent"""
        return self.storage_path / f"{agent_id}_memory.json"

    async def _load_agent_memory(self, agent_id: str) -> Dict[str, Dict]:
        """Load agent memory from file"""
        file_path = self._get_agent_file(agent_id)
        if not file_path.exists():
            return {}
        try:
            with open(file_path, 'r', encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            self.logger.error(f"Failed to load memory for {agent_id}: {e}")
            return {}

    async def _save_agent_memory(self, agent_id: str, memory_data: Dict[str, Dict]) -> bool:
        """Save agent memory to file"""
        file_path = self._get_agent_file(agent_id)
        try:
            with open(file_path, 'w', encoding="utf-8") as f:
                json.dump(memory_data, f, indent=2, default=str)
            return True
        except IOError as e:
            self.logger.error(f"Failed to save memory for {agent_id}: {e}")
            return False

    async def store(self, entry: MemoryEntry) -> bool:
        """Store a memory entry"""
        memory_data = await self._load_agent_memory(entry.agent_id)
        entry_dict = {
            "value": entry.value,
            "timestamp": entry.timestamp.isoformat(),
            "memory_type": entry.memory_type,
            "ttl": entry.ttl,
            "tags": entry.tags or []
        }
        memory_data[entry.key] = entry_dict
        return await self._save_agent_memory(entry.agent_id, memory_data)

    async def retrieve(self, key: str, agent_id: Optional[str] = None) -> Optional[MemoryEntry]:
        """Retrieve a memory entry"""
        if not agent_id:
            # Search across all agents
            for agent_file in self.storage_path.glob("*_memory.json"):
                agent_id_from_file = agent_file.stem.replace("_memory", "")
                memory_data = await self._load_agent_memory(agent_id_from_file)
                if key in memory_data:
                    return self._dict_to_entry(key, agent_id_from_file, memory_data[key])
            return None
        else:
            memory_data = await self._load_agent_memory(agent_id)
            if key in memory_data:
                return self._dict_to_entry(key, agent_id, memory_data[key])
            return None

    def _dict_to_entry(self, key: str, agent_id: str, entry_dict: Dict) -> MemoryEntry:
        """Convert dictionary back to MemoryEntry"""
        return MemoryEntry(
            key=key,
            value=entry_dict["value"],
            agent_id=agent_id,
            timestamp=datetime.fromisoformat(entry_dict["timestamp"]),
            memory_type=entry_dict.get("memory_type", "general"),
            ttl=entry_dict.get("ttl"),
            tags=entry_dict.get("tags", [])
        )

    async def search(self, query: Dict[str, Any]) -> List[MemoryEntry]:
        """Search memory entries by criteria"""
        results = []
        agent_id_filter = query.get("agent_id")
        memory_type_filter = query.get("memory_type")
        tag_filter = query.get("tags", [])

        # Determine which agent files to search
        if agent_id_filter:
            agent_files = [self._get_agent_file(agent_id_filter)]
        else:
            agent_files = list(self.storage_path.glob("*_memory.json"))

        for agent_file in agent_files:
            if not agent_file.exists():
                continue
            agent_id = agent_file.stem.replace("_memory", "")
            memory_data = await self._load_agent_memory(agent_id)
            for key, entry_dict in memory_data.items():
                if memory_type_filter and entry_dict.get("memory_type") != memory_type_filter:
                    continue
                if tag_filter:
                    entry_tags = set(entry_dict.get("tags", []))
                    if not set(tag_filter).intersection(entry_tags):
                        continue
                results.append(self._dict_to_entry(key, agent_id, entry_dict))
        return results

    async def delete(self, key: str, agent_id: Optional[str] = None) -> bool:
        """Delete a memory entry"""
        if not agent_id:
            deleted = False
            for agent_file in self.storage_path.glob("*_memory.json"):
                agent_id_from_file = agent_file.stem.replace("_memory", "")
                memory_data = await self._load_agent_memory(agent_id_from_file)
                if key in memory_data:
                    del memory_data[key]
                    await self._save_agent_memory(agent_id_from_file, memory_data)
                    deleted = True
            return deleted
        else:
            memory_data = await self._load_agent_memory(agent_id)
            if key in memory_data:
                del memory_data[key]
                return await self._save_agent_memory(agent_id, memory_data)
            return False

class AgentMemoryManager:
    """High-level memory manager for agents"""

    def __init__(self, backend: MemoryBackend = None):
        self.backend = backend or FileMemoryBackend()
        self.logger = logging.getLogger("arable.agents.memory")

    async def store_agent_memory(self, agent_id: str, key: str, value: Any,
                                memory_type: str = "general", ttl: Optional[int] = None,
                                tags: List[str] = None) -> bool:
        """Store memory for a specific agent"""
        entry = MemoryEntry(
            key=key,
            value=value,
            agent_id=agent_id,
            timestamp=datetime.now(),
            memory_type=memory_type,
            ttl=ttl,
            tags=tags or []
        )
        success = await self.backend.store(entry)
        if success:
            self.logger.debug(f"Stored memory for {agent_id}: {key}")
        else:
            self.logger.error(f"Failed to store memory for {agent_id}: {key}")
        return success

    async def get_agent_memory(self, agent_id: str, key: str) -> Any:
        """Get memory value for a specific agent"""
        entry = await self.backend.retrieve(key, agent_id)
        return entry.value if entry else None

    async def share_memory(self, from_agent: str, to_agent: str, key: str,
                          new_key: Optional[str] = None) -> bool:
        """Share memory between agents"""
        source_entry = await self.backend.retrieve(key, from_agent)
        if not source_entry:
            self.logger.warning(f"No memory found for {from_agent}:{key}")
            return False
        target_key = new_key or key
        shared_entry = MemoryEntry(
            key=target_key,
            value=source_entry.value,
            agent_id=to_agent,
            timestamp=datetime.now(),
            memory_type="shared",
            tags=["shared_from", from_agent]
        )
        success = await self.backend.store(shared_entry)
        if success:
            self.logger.info(f"Shared memory {from_agent}:{key} -> {to_agent}:{target_key}")
        return success

    async def get_workflow_memory(self, workflow_id: str) -> Dict[str, Any]:
        """Get all memory entries related to a workflow"""
        entries = await self.backend.search({
            "tags": ["workflow", workflow_id]
        })
        workflow_memory = {}
        for entry in entries:
            workflow_memory[f"{entry.agent_id}:{entry.key}"] = entry.value
        return workflow_memory

    async def store_workflow_result(self, workflow_id: str, agent_id: str,
                                   task_id: str, result: Any) -> bool:
        """Store workflow task result for inter-agent access"""
        return await self.store_agent_memory(
            agent_id=agent_id,
            key=f"workflow_result_{task_id}",
            value=result,
            memory_type="workflow_result",
            tags=["workflow", workflow_id, "task_result"]
        )

    async def cleanup_expired_memory(self) -> int:
        """Clean up expired memory entries based on TTL"""
        # Placeholder - TTL cleanup not yet implemented
        return 0

    async def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory usage statistics"""
        all_entries = await self.backend.search({})
        stats = {
            "total_entries": len(all_entries),
            "agents_with_memory": len(set(entry.agent_id for entry in all_entries)),
            "memory_types": {},
            "memory_by_agent": {}
        }
        for entry in all_entries:
            stats["memory_types"].setdefault(entry.memory_type, 0)
            stats["memory_types"][entry.memory_type] += 1
            stats["memory_by_agent"].setdefault(entry.agent_id, 0)
            stats["memory_by_agent"][entry.agent_id] += 1
        return stats

# Global memory manager instance
memory_manager = AgentMemoryManager()
