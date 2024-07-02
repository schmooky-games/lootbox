import json

import pytest
from collections import defaultdict
from fastapi.testclient import TestClient
from redis import Redis

from src.config import REDIS_URI
from src.main import app

client = TestClient(app)

redis = Redis.from_url(url=REDIS_URI)


@pytest.fixture
def setup_lootbox():
    payload = [
        {"data": {"value": "item1"}, "meta": {"name": "Item 1"}},
        {"data": {"value": "item2"}, "meta": {"name": "Item 2"}},
        {"data": {"value": "item3"}, "meta": {"name": "Item 3"}}
    ]
    response = client.post("/equal/create_lootbox", json=payload)
    assert response.status_code == 200
    lootbox = response.json()

    redis.set(lootbox["id"], json.dumps(lootbox))

    yield lootbox

    redis.delete(lootbox["id"])


def test_get_loot_randomness(setup_lootbox):
    lootbox = setup_lootbox
    lootbox_id = lootbox["id"]

    num_tests = 100

    item_counts = defaultdict(int)

    for _ in range(num_tests):
        response = client.get(f"/equal/get_loot/{lootbox_id}")
        assert response.status_code == 200
        item = response.json()

        stored_lootbox = json.loads(redis.get(lootbox_id))

        for lootbox_item in stored_lootbox["items"]:
            if item == lootbox_item:
                item_counts[item["meta"]["name"]] += 1
                break

    print("Statistics:")
    for item_name, count in item_counts.items():
        print(f"{item_name}: {count}")

    for lootbox_item in stored_lootbox["items"]:
        assert lootbox_item["meta"]["name"] in item_counts
