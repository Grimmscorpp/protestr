import unittest
from protestr import resolve
from protestr.specs import between, either, subset, sequence
from random import random
from types import GeneratorType


class TestResolver(unittest.TestCase):
    def test_resolve(self):
        intgr = resolve(int)
        assert isinstance(intgr, int)
        assert 0 <= intgr <= 1000

        real = resolve(float)
        assert isinstance(real, float)
        assert 0 <= real <= 1000

        complx = resolve(complex)
        assert isinstance(complx, complex)
        assert -1000 <= complx.real <= 1000
        assert -1000 <= complx.imag <= 1000

        booln = resolve(bool)
        assert isinstance(booln, bool)
        assert booln in (True, False)

        word = resolve(str)
        assert all("a" <= c <= "z" or "A" <= c <= "Z" for c in word)

        intgr = resolve(between(-20, 20))
        assert isinstance(intgr, int)
        assert -20 <= intgr <= 20

        real = resolve(between(-20.0, 20))
        assert isinstance(real, float)
        assert -20 <= real <= 20

        assert 0 <= resolve(either(*range(3))) < 3
        sub = resolve(subset(range(3), n=2))
        assert len(sub) == 2
        assert all(x in range(3) for x in sub)

        seq = resolve(sequence(int, 3))
        assert isinstance(seq, GeneratorType)
        assert len(tuple(seq)) == 3
        assert all(isinstance(x, int) for x in seq)

        seq = resolve(sequence(int, 3, type=tuple))
        assert isinstance(seq, tuple)
        assert len(seq) == 3
        assert all(isinstance(x, int) for x in seq)

        dictnry = resolve(dict(key=str))
        assert isinstance(dictnry, dict)
        assert len(dictnry) == 1
        assert isinstance(dictnry["key"], str)

        assert resolve(random) < 1

        assert resolve("lit") == "lit"


if __name__ == "__main__":
    unittest.main()
