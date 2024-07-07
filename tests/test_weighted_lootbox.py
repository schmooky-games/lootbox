import json
import pytest
from collections import defaultdict
from fastapi.testclient import TestClient
from redis import Redis

from src.config import REDIS_URI, TEMP_TOKEN
from src.main import app

client = TestClient(app)

redis = Redis.from_url(url=REDIS_URI)

headers = {
    "Authorization": f"Bearer {TEMP_TOKEN}"
}


@pytest.fixture
def setup_lootbox():
    payload = [
        {"data": {"value": "item1"}, "meta": {"name": "Item 1"}, "weight": "500"},
        {"data": {"value": "item2"}, "meta": {"name": "Item 2"}, "weight": "100"},
        {"data": {"value": "item3"}, "meta": {"name": "Item 3"}, "weight": "100"},
        {"data": {"value": "item4"}, "meta": {"name": "Item 4"}, "weight": "50"},
        {"data": {"value": "item5"}, "meta": {"name": "Item 5"}, "weight": "50"}
    ]
    response = client.post("/weighted/create_lootbox", json=payload, headers=headers)
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
        response = client.get(f"/weighted/get_loot/{lootbox_id}", headers=headers)
        assert response.status_code == 200
        item = response.json()

        stored_lootbox = json.loads(redis.get(lootbox_id))

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
