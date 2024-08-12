import numpy as np

from src.lootboxes.schemas import Lootbox


def simulate_equal_lootbox_draws(lootbox: Lootbox, num_draws: int) -> str:
    draws = np.random.choice(
        a=range(len(lootbox.items)),
        size=num_draws,
        replace=True
    )

    return ''.join(format(draw, f'0{len(lootbox.items)}b') for draw in draws)


def simulate_weighted_lootbox_draws(lootbox: Lootbox, num_draws: int) -> str:
    weights = np.array([item.weight for item in lootbox.items])
    normalized_weights = weights / np.sum(weights)

    draws = np.random.choice(
        a=range(len(lootbox.items)),
        size=num_draws,
        replace=True,
        p=normalized_weights
    )

    binary_strings = [bin(draw)[2:] for draw in draws]
    return ''.join(binary_strings)
    # bitstring = ''.join(format(draw, f'0{len(lootbox.items)}b') for draw in draws)
    #
    # with open(filename, 'w') as file:
    #     file.write(bitstring)


# lootbox = Lootbox(
#         id="test_lootbox",
#         is_active=True,
#         items=[
#             WeightedItem(id="1", data={"value": "item 1"}, meta={"name": "Item1"}, weight=500.0),
#             WeightedItem(id="2", data={"value": "item 2"}, meta={"name": "Item2"}, weight=100.0),
#             WeightedItem(id="3", data={"value": "item 3"}, meta={"name": "Item3"}, weight=100.0),
#             WeightedItem(id="4", data={"value": "item 4"}, meta={"name": "Item4"}, weight=50.0),
#             WeightedItem(id="5", data={"value": "item 5"}, meta={"name": "Item5"}, weight=50.0)
#         ]
#     )
#
# simulate_weighted_lootbox_draws(lootbox, 1000000, 'bitstring_output.txt')


def run_nist_tests(bitstring: str):
    from tests.nist.NIST_Tests import NIST_Tests

    nist_tests = NIST_Tests()
    results = nist_tests.run(bitstring)

    for test_name, result in results.items():
        if isinstance(result, tuple):
            p_value = result[0]
        else:
            p_value = result

        if isinstance(p_value, (float, int)):
            if p_value >= 0.01:
                print(f"{test_name}: Pass (p-value: {p_value})")
            else:
                print(f"{test_name}: Fail (p-value: {p_value})")
        else:
            print(f"{test_name}: Inconclusive (p-value: {p_value})")

    return results
