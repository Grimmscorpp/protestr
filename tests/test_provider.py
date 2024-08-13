import unittest
from unittest.mock import patch, call
from protestr import provide
from protestr.specs import between, either, subset, sequence
from random import random


class TestProvider(unittest.TestCase):
    @patch("protestr.resolve")
    def test_provide(self, resolve):
        def orig_func(*args, **kwds): return args, kwds

        (intgr,), kwds = provide(
            int, real=float, complx=complex, booln=bool, word=str,
            int_btween=between(-20, 20), real_btween=between(-20, 20.0),
            choice=either(*range(3)), sub=subset(range(3), 2),
            gen=sequence(int, 3), tup=sequence(str, 3, tuple),
            dictnry={str: str}, rand=random, lit="lit"
        )(orig_func)()

        assert isinstance(kwds, dict)
        assert list(kwds) == [
            "real", "complx", "booln", "word", "int_btween",
            "real_btween", "choice", "sub", "gen", "tup", "dictnry",
            "rand", "lit"
        ]

        expected_calls = [
            call(float), call(complex), call(bool), call(str),
            call(between(-20, 20)), call(between(-20.0, 20.0)),
            call(either(*range(3))), call(subset(range(3), 2)),
            call(sequence(int, 3)), call(sequence(str, 3, tuple)),
            call({str: str}), call(random), call("lit"), call(int)
        ]

        assert resolve.call_count == len(expected_calls)
        resolve.assert_has_calls(expected_calls)


if __name__ == "__main__":
    unittest.main()
