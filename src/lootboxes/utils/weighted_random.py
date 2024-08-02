import secrets
from bisect import bisect_right
from itertools import accumulate


def weighted_random(items, weights):
    cumulative_weights = list(accumulate(weights))
    total = cumulative_weights[-1]
    random_value = secrets.randbelow(int(total * 1000000)) / 1000000
    index = bisect_right(cumulative_weights, random_value)
    return items[index]
