import secrets
from bisect import bisect_right
from collections import Counter
from itertools import accumulate

arr = ["item1", "item2", "item3", "item4", "item5"]
w = [500.0, 100.0, 100.0, 50.0, 50.0]


def weighted_random(items, weights):
    cumulative_weights = list(accumulate(weights))
    total = cumulative_weights[-1]
    random_value = secrets.randbelow(int(total * 1000000)) / 1000000
    index = bisect_right(cumulative_weights, random_value)
    return items[index]


counter = Counter()
for _ in range(5000000):
    result = weighted_random(arr, w)
    counter[result] += 1


for item in arr:
    print(f"{item}: {counter[item]}")
