# src/core/flow_manager.py
"""Manages flows: load, list, add, update, delete."""

from typing import List, Optional

from .storage import Storage
from .flow import Flow


class FlowManager:
    """
    Manages flows. Loads from storage on each request (no in-memory cache).
    """

    def __init__(self, storage: Storage):
        self.storage = storage

    def get_flow(self, flow_id: str) -> Optional[Flow]:
        """Return flow by ID. Returns None if not found."""
        return self.storage.load_flow(flow_id)

    def list_flows(self, tag: Optional[str] = None) -> List[Flow]:
        """List all flows, optionally filtered by tag."""
        flows = self.storage.load_flows()
        if tag is not None:
            tag_lower = tag.lower()
            flows = [f for f in flows if any(tag_lower in t.lower() for t in f.tags)]
        return flows

    def add_flow(self, flow: Flow) -> None:
        """Save a new flow. Overwrites if flow_id already exists."""
        self.storage.save_flow(flow)

    def update_flow(self, flow_id: str, flow: Flow) -> bool:
        """Update an existing flow. Flow.id must match flow_id. Returns True if flow existed."""
        if not self.storage.flow_exists(flow_id):
            return False
        if flow.id != flow_id:
            # If ID changed, remove old file
            self.storage.delete_flow(flow_id)
        self.storage.save_flow(flow)
        return True

    def delete_flow(self, flow_id: str) -> bool:
        """Delete a flow. Returns True if the flow existed and was removed."""
        return self.storage.delete_flow(flow_id)

    def search_flows(self, query: Optional[str] = None, tag: Optional[str] = None) -> List[Flow]:
        """Search flows by optional query (name, description, id) and/or tag."""
        flows = self.list_flows(tag=tag)
        if query is None or query == "":
            return flows
        q = query.lower()
        return [
            f
            for f in flows
            if q in f.id.lower()
            or q in f.name.lower()
            or q in f.description.lower()
            or any(q in t.lower() for t in f.tags)
        ]
