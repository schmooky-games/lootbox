from src.lootboxes.equal.schemas import Item, Lootbox
from tests.nist.utils import simulate_equal_lootbox_draws, run_nist_tests


def test_weighted_lootbox():
    print("\n")
    lootbox = Lootbox(
        id="test_lootbox",
        is_active=True,
        items=[
            Item(id="1", data={"value": "item 1"}, meta={"name": "Item1"}),
            Item(id="2", data={"value": "item 2"}, meta={"name": "Item2"}),
            Item(id="3", data={"value": "item 3"}, meta={"name": "Item3"}),
            Item(id="4", data={"value": "item 4"}, meta={"name": "Item4"}),
        ]
    )

    num_draws = 1_000_000
    bitstring = simulate_equal_lootbox_draws(lootbox, num_draws)

    results = run_nist_tests(bitstring)


if __name__ == "__main__":
    test_weighted_lootbox()
