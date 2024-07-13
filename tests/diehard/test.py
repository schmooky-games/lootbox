import secrets

random_numbers = [secrets.randbelow(2 ** 32) for _ in range(1000000)]

with open('rn.txt', 'w') as f:
    for num in random_numbers:
        f.write(str(num) + '\n')
