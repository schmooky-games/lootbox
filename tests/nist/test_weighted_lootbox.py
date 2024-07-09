from src.lootboxes.schemas import WeightedItem, Lootbox
from tests.nist.utils import simulate_weighted_lootbox_draws, run_nist_tests


def test_weighted_lootbox():
    print("\n")
    lootbox = Lootbox(
        id="test_lootbox",
        is_active=True,
        items=[
            WeightedItem(id="1", data={"value": "item 1"}, meta={"name": "Item1"}, weight=500.0),
            WeightedItem(id="2", data={"value": "item 2"}, meta={"name": "Item2"}, weight=100.0),
            WeightedItem(id="3", data={"value": "item 3"}, meta={"name": "Item3"}, weight=100.0),
            WeightedItem(id="4", data={"value": "item 4"}, meta={"name": "Item4"}, weight=50.0),
            # WeightedItem(id="5", data={"value": "item 5"}, meta={"name": "Item5"}, weight=50.0)
        ]
    )

    num_draws = 1_000_000
    bitstring = simulate_weighted_lootbox_draws(lootbox, num_draws)

    results = run_nist_tests(bitstring)


if __name__ == "__main__":
    test_weighted_lootbox()
