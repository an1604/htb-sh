# tests/test_flow_manager.py
"""Tests for FlowManager."""

import pytest
from src.core.flow_manager import FlowManager
from src.core.flow import Flow, FlowStep
from src.core.command import Parameter


class TestFlowManager:
    """Test FlowManager."""

    @pytest.fixture
    def manager(self, storage):
        return FlowManager(storage)

    def test_get_flow_nonexistent(self, manager):
        """Test get_flow returns None for missing flow."""
        assert manager.get_flow("no-such-flow") is None

    def test_get_flow_exists(self, manager, sample_flow):
        """Test get_flow returns flow when it exists."""
        manager.add_flow(sample_flow)
        loaded = manager.get_flow(sample_flow.id)
        assert loaded is not None
        assert loaded.id == sample_flow.id
        assert loaded.name == sample_flow.name

    def test_list_flows_empty(self, manager):
        """Test list_flows returns empty list when no flows."""
        assert manager.list_flows() == []

    def test_list_flows_with_tag_filter(self, manager, sample_flow):
        """Test list_flows filters by tag."""
        manager.add_flow(sample_flow)
        flow2 = Flow(
            id="web-flow",
            name="Web",
            description="Web recon",
            steps=[],
            flow_parameters=[],
            tags=["web", "reconnaissance"],
        )
        manager.add_flow(flow2)
        all_flows = manager.list_flows()
        assert len(all_flows) == 2
        enum_flows = manager.list_flows(tag="enumeration")
        assert len(enum_flows) == 1
        assert enum_flows[0].id == "smb-enumeration"
        web_flows = manager.list_flows(tag="web")
        assert len(web_flows) == 1
        assert web_flows[0].id == "web-flow"

    def test_add_flow(self, manager, sample_flow):
        """Test add_flow persists flow."""
        manager.add_flow(sample_flow)
        assert manager.get_flow(sample_flow.id) is not None

    def test_update_flow(self, manager, sample_flow):
        """Test update_flow modifies existing flow."""
        manager.add_flow(sample_flow)
        sample_flow.name = "Updated SMB Enumeration"
        sample_flow.description = "Updated description"
        result = manager.update_flow(sample_flow.id, sample_flow)
        assert result is True
        loaded = manager.get_flow(sample_flow.id)
        assert loaded.name == "Updated SMB Enumeration"
        assert loaded.description == "Updated description"

    def test_update_flow_nonexistent(self, manager, sample_flow):
        """Test update_flow on non-existent flow returns False."""
        result = manager.update_flow("no-such-id", sample_flow)
        assert result is False

    def test_delete_flow(self, manager, sample_flow):
        """Test delete_flow removes flow."""
        manager.add_flow(sample_flow)
        result = manager.delete_flow(sample_flow.id)
        assert result is True
        assert manager.get_flow(sample_flow.id) is None

    def test_delete_flow_nonexistent(self, manager):
        """Test delete_flow on non-existent returns False."""
        assert manager.delete_flow("no-such-flow") is False

    def test_search_flows_empty_query_returns_all(self, manager, sample_flow):
        """Test search_flows with no query returns all (or filtered by tag)."""
        manager.add_flow(sample_flow)
        results = manager.search_flows()
        assert len(results) == 1
        results = manager.search_flows(query="")
        assert len(results) == 1

    def test_search_flows_by_query(self, manager, sample_flow):
        """Test search_flows filters by query in id, name, description, tags."""
        manager.add_flow(sample_flow)
        assert len(manager.search_flows(query="smb")) == 1
        assert len(manager.search_flows(query="SMB Enumeration")) == 1
        assert len(manager.search_flows(query="List shares")) == 1
        assert len(manager.search_flows(query="enumeration")) == 1
        assert len(manager.search_flows(query="nonexistent")) == 0

    def test_search_flows_by_tag(self, manager, sample_flow):
        """Test search_flows with tag filter."""
        manager.add_flow(sample_flow)
        assert len(manager.search_flows(tag="smb")) == 1
        assert len(manager.search_flows(tag="web")) == 0
