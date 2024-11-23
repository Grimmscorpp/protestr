import unittest
from unittest.mock import MagicMock
from protestr import provide
from examples.lib import cached
from examples.specs import Redis


class TestWithRedis(unittest.TestCase):
    @provide(
        Redis,
        response={str: str},
    )
    @provide(response=None)
    def test_cached_should_cache_fn(self, response):
        costly_computation = MagicMock()

        @cached
        def fn():
            costly_computation()
            return response

        self.assertEqual(response, fn())
        self.assertEqual(response, fn())

        costly_computation.assert_called_once()


if __name__ == "__main__":
    unittest.main()
