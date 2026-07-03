"""Tests de backpressure y drop policies de EventQueue."""

import asyncio

import pytest

from bidiwave.events.queue import EventQueue


@pytest.mark.asyncio
async def test_drop_oldest_discards_oldest():
    queue = EventQueue(max_size=2, drop_policy="oldest")
    await queue.put({"id": 1})
    await queue.put({"id": 2})
    await queue.put({"id": 3})

    assert queue.qsize() == 2
    first = await queue.get()
    assert first["id"] == 2
    second = await queue.get()
    assert second["id"] == 3
    assert queue.dropped_count == 1


@pytest.mark.asyncio
async def test_drop_newest_keeps_oldest():
    queue = EventQueue(max_size=2, drop_policy="newest")
    await queue.put({"id": 1})
    await queue.put({"id": 2})
    await queue.put({"id": 3})

    assert queue.qsize() == 2
    first = await queue.get()
    assert first["id"] == 1
    second = await queue.get()
    assert second["id"] == 2
    assert queue.dropped_count == 1


@pytest.mark.asyncio
async def test_drop_block_blocks_until_space():
    queue = EventQueue(max_size=1, drop_policy="block")
    await queue.put({"id": 1})

    async def consumer():
        await asyncio.sleep(0.05)
        return await queue.get()

    consumer_task = asyncio.create_task(consumer())
    await asyncio.sleep(0.01)
    await queue.put({"id": 2})

    item = await consumer_task
    assert item["id"] == 1
    assert queue.dropped_count == 0


@pytest.mark.asyncio
async def test_dropped_count_increments():
    queue = EventQueue(max_size=1, drop_policy="oldest")
    await queue.put({"id": 1})
    await queue.put({"id": 2})
    await queue.put({"id": 3})
    assert queue.dropped_count == 2


@pytest.mark.asyncio
async def test_no_drop_when_under_limit():
    queue = EventQueue(max_size=5, drop_policy="oldest")
    await queue.put({"id": 1})
    await queue.put({"id": 2})
    assert queue.dropped_count == 0
    assert queue.qsize() == 2
