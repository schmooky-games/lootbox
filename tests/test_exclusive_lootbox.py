import json
import pytest
from collections import defaultdict
from httpx import AsyncClient
import pytest_asyncio

from src.main import app
from src.redis_connection import redis


@pytest_asyncio.fixture
async def async_client():
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest_asyncio.fixture
async def setup_lootbox(async_client):
    payload = [
        {"data": {"value": "item1"}, "meta": {"name": "Item 1"}, "weight": "500"},
        {"data": {"value": "item2"}, "meta": {"name": "Item 2"}, "weight": "100"},
        {"data": {"value": "item3"}, "meta": {"name": "Item 3"}, "weight": "100"},
        {"data": {"value": "item4"}, "meta": {"name": "Item 4"}, "weight": "50"},
        {"data": {"value": "item5"}, "meta": {"name": "Item 5"}, "weight": "50"},
        {"data": {"value": "item6"}, "meta": {"name": "Item 6"}, "weight": "50"},
        {"data": {"value": "item7"}, "meta": {"name": "Item 7"}, "weight": "50"},
        {"data": {"value": "item8"}, "meta": {"name": "Item 8"}, "weight": "50"},
        {"data": {"value": "item9"}, "meta": {"name": "Item 9"}, "weight": "50"},
        {"data": {"value": "item0"}, "meta": {"name": "Item 0"}, "weight": "50"}
    ]
    response = await async_client.post("/exclusive/create_lootbox", json=payload)
    assert response.status_code == 200
    lootbox = response.json()

    await redis.set(lootbox["id"], json.dumps(lootbox))

    yield lootbox

    await redis.delete(lootbox["id"])


@pytest.mark.asyncio
async def test_get_loot_uniqueness(async_client, setup_lootbox):
    lootbox = setup_lootbox
    lootbox_id = lootbox["id"]

    item_counts = defaultdict(int)
    original_items = set()

    stored_lootbox = json.loads(await redis.get(lootbox_id))
    for item in stored_lootbox["items"]:
        original_items.add(item["meta"]["name"])

    while len(item_counts) < len(original_items):
        response = await async_client.get(f"/exclusive/get_loot/{lootbox_id}")
        assert response.status_code == 200
        item = response.json()
        item_name = item["meta"]["name"]
        item_counts[item_name] += 1

    print("Statistics:")
    sorted_item_count = dict(sorted(item_counts.items()))
    for item_name, count in sorted_item_count.items():
        print(f"{item_name}: {count}")

    for item_name in original_items:
        assert item_counts[item_name] == 1

    final_lootbox = json.loads(await redis.get(lootbox_id))
    assert len(final_lootbox["items"]) == 0
