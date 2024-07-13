from secrets import randbits
from NIST_Tests import NIST_Tests
from tests.nist.utils import run_nist_tests

nist_tests = NIST_Tests()


def test_random():
    print("\n")
    bts = str(bin(randbits(1_000_000)))

    results = run_nist_tests(bts[2:])
