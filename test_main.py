import pytest
from collections import defaultdict
from fastapi.testclient import TestClient

from main import lootboxes, app

client = TestClient(app)


@pytest.fixture
def setup_lootbox():
    payload = [
        {"data": {"value": "item1"}, "meta": {"name": "Item 1"}},
        {"data": {"value": "item2"}, "meta": {"name": "Item 2"}},
        {"data": {"value": "item3"}, "meta": {"name": "Item 3"}}
    ]
    response = client.post("/create_lootbox", json=payload)
    assert response.status_code == 200
    lootbox = response.json()
    yield lootbox
    if lootbox["id"] in lootboxes:
        lootboxes.pop(lootbox["id"], None)


def test_get_loot_randomness(setup_lootbox):
    lootbox = setup_lootbox
    lootbox_id = lootbox["id"]

    num_tests = 100

    item_counts = defaultdict(int)

    for _ in range(num_tests):
        response = client.get(f"/get_loot/{lootbox_id}")
        assert response.status_code == 200
        item = response.json()

        for lootbox_item in lootbox["items"]:
            if item == lootbox_item:
                item_counts[item["meta"]["name"]] += 1
                break

    print("Statistics:")
    for item_name, count in item_counts.items():
        print(f"{item_name}: {count}")

    for lootbox_item in lootbox["items"]:
        assert lootbox_item["meta"]["name"] in item_counts
