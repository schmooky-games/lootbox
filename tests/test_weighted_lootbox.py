import json
from collections import defaultdict

import pytest
import pytest_asyncio
from httpx import AsyncClient

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
        {"data": {"value": "item5"}, "meta": {"name": "Item 5"}, "weight": "50"}
    ]
    response = await async_client.post("/weighted/create_lootbox", json=payload)
    assert response.status_code == 200
    lootbox = response.json()

    await redis.set(lootbox["id"], json.dumps(lootbox))

    yield lootbox

    await redis.delete(lootbox["id"])


@pytest.mark.asyncio
async def test_get_loot_randomness(async_client, setup_lootbox):
    lootbox = setup_lootbox
    lootbox_id = lootbox["id"]

    num_tests = 100

    item_counts = defaultdict(int)

    for _ in range(num_tests):
        response = await async_client.get(f"/weighted/get_loot/{lootbox_id}")
        assert response.status_code == 200
        item = response.json()

        stored_lootbox = json.loads(await redis.get(lootbox_id))

        for lootbox_item in stored_lootbox["items"]:
            if item == lootbox_item:
                item_counts[item["meta"]["name"]] += 1
                break

    print("Statistics:")
    sorted_item_counts = dict(sorted(item_counts.items()))
    for item_name, count in sorted_item_counts.items():
        print(f"{item_name}: {count}")

    for lootbox_item in stored_lootbox["items"]:
        assert lootbox_item["meta"]["name"] in item_counts
