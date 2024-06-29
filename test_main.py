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
    yield lootbox  # Возвращаем сам lootbox, а не только id
    if lootbox["id"] in lootboxes:
        lootboxes.pop(lootbox["id"], None)


def test_get_loot_randomness(setup_lootbox):
    lootbox = setup_lootbox
    lootbox_id = lootbox["id"]

    # Количество тестов, которые мы хотим выполнить для получения статистики
    num_tests = 100

    # Словарь для подсчета выпадений предметов
    item_counts = defaultdict(int)

    # Выполняем тесты num_tests раз
    for _ in range(num_tests):
        # Получаем предмет из лутбокса
        response = client.get(f"/get_loot/{lootbox_id}")
        assert response.status_code == 200
        item = response.json()

        # Увеличиваем счетчик выпадений данного предмета
        for lootbox_item in lootbox["items"]:
            if item == lootbox_item:
                item_counts[item["meta"]["name"]] += 1
                break  # Дополнительные предметы не нужны для подсчета

    # Выводим результаты статистики в консоль
    print("Statistics:")
    for item_name, count in item_counts.items():
        print(f"{item_name}: {count}")

    # Проверяем, что все предметы выпадали хотя бы один раз
    for lootbox_item in lootbox["items"]:
        assert lootbox_item["meta"]["name"] in item_counts
