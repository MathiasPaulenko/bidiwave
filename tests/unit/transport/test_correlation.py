"""Tests unitarios para transport/correlation.py."""

import pytest

from bidiwave.exceptions import BiDiConnectionError
from bidiwave.transport.correlation import Correlator


class TestCorrelator:
    def test_next_id_incremental(self) -> None:
        corr = Correlator()
        assert corr.next_id() == 1
        assert corr.next_id() == 2
        assert corr.next_id() == 3

    @pytest.mark.asyncio
    async def test_register_and_resolve(self) -> None:
        corr = Correlator()
        fut = corr.register(1)
        assert not fut.done()
        corr.resolve(1, {"sessionId": "abc"})
        result = await fut
        assert result == {"sessionId": "abc"}

    @pytest.mark.asyncio
    async def test_register_and_reject(self) -> None:
        corr = Correlator()
        fut = corr.register(1)
        corr.reject(1, RuntimeError("boom"))
        with pytest.raises(RuntimeError, match="boom"):
            await fut

    @pytest.mark.asyncio
    async def test_reject_all(self) -> None:
        corr = Correlator()
        fut1 = corr.register(1)
        fut2 = corr.register(2)
        corr.reject_all(BiDiConnectionError("closed"))
        with pytest.raises(BiDiConnectionError, match="closed"):
            await fut1
        with pytest.raises(BiDiConnectionError, match="closed"):
            await fut2

    @pytest.mark.asyncio
    async def test_resolve_unknown_id_is_noop(self) -> None:
        corr = Correlator()
        corr.resolve(999, {"foo": "bar"})  # should not raise

    @pytest.mark.asyncio
    async def test_reject_unknown_id_is_noop(self) -> None:
        corr = Correlator()
        corr.reject(999, RuntimeError("x"))  # should not raise
