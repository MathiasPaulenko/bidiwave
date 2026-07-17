"""Regression tests for Phase 2 stabilization fixes — round 4.

Each test class corresponds to a specific fix applied during the
continued complete static review phase.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from bidiwave.modules.browsing import BrowsingModule

MockConn = MagicMock

CTX_ID = "ctx-1"


@pytest.fixture
def mock_connection() -> MockConn:
    conn = MagicMock()
    conn.send_command = AsyncMock()
    return conn


@pytest.fixture
def browsing_module(mock_connection: MockConn) -> BrowsingModule:
    return BrowsingModule(mock_connection)


class TestWaitForSelectorSafeStringEmbedding:
    """Fix: wait_for_selector used repr() to embed the selector into a JS
    expression. repr() produces Python literal syntax, which is not
    guaranteed to be valid/safe JavaScript for all inputs. json.dumps()
    is used instead, which is guaranteed to produce a valid JS string
    literal for any Python str input.
    """

    async def test_selector_with_single_quote(
        self,
        browsing_module: BrowsingModule,
        mock_connection: MockConn,
    ) -> None:
        mock_connection.send_command.return_value = {
            "type": "success",
            "result": {"type": "boolean", "value": True},
        }
        await browsing_module.wait_for_selector(CTX_ID, "div[data-foo='bar']")
        params = mock_connection.send_command.call_args.args[1]
        expr = params["expression"]
        assert '"div[data-foo=\'bar\']"' in expr

    async def test_selector_with_double_quote(
        self,
        browsing_module: BrowsingModule,
        mock_connection: MockConn,
    ) -> None:
        mock_connection.send_command.return_value = {
            "type": "success",
            "result": {"type": "boolean", "value": True},
        }
        await browsing_module.wait_for_selector(CTX_ID, 'div[data-foo="bar"]')
        params = mock_connection.send_command.call_args.args[1]
        expr = params["expression"]
        # json.dumps escapes embedded double quotes with backslash
        assert '\\"bar\\"' in expr

    async def test_selector_with_both_quote_types(
        self,
        browsing_module: BrowsingModule,
        mock_connection: MockConn,
    ) -> None:
        mock_connection.send_command.return_value = {
            "type": "success",
            "result": {"type": "boolean", "value": True},
        }
        selector = """div[title="it's \\"quoted\\""]"""
        await browsing_module.wait_for_selector(CTX_ID, selector)
        params = mock_connection.send_command.call_args.args[1]
        expr = params["expression"]
        # The expression must be valid JS: verify it round-trips through
        # json.loads to reconstruct the original selector exactly once
        # embedded as a JS/JSON string literal.
        import json
        import re

        matches = re.findall(r"document\.querySelector\((\".*?\")\)", expr)
        assert matches
        assert json.loads(matches[0]) == selector

    async def test_selector_unicode(
        self,
        browsing_module: BrowsingModule,
        mock_connection: MockConn,
    ) -> None:
        mock_connection.send_command.return_value = {
            "type": "success",
            "result": {"type": "boolean", "value": True},
        }
        selector = "div[data-emoji='🚀']"
        await browsing_module.wait_for_selector(CTX_ID, selector)
        params = mock_connection.send_command.call_args.args[1]
        expr = params["expression"]
        assert "🚀" in expr or "\\ud83d\\ude80" in expr
