import unittest
from unittest.mock import patch, call
from protestr import provide


class TestProvider(unittest.TestCase):
    @patch("protestr.resolve")
    def test_provide_should_return_the_last_result(self, resolve):
        calls = 0

        @provide()
        @provide()
        def fn():
            nonlocal calls
            calls += 1
            return calls

        self.assertEqual(2, fn())

    @patch("protestr.resolve")
    def test_provide_should_inject_keyword_specs(self, resolve):
        resolve.side_effect = lambda x: x

        @provide(0, x=1)
        def fn(x):
            return x

        self.assertEqual(1, fn())
        self.assertEqual(resolve.mock_calls, [call(0), call(1)])

    @patch("protestr.resolve")
    def test_provide_should_patch_the_first_fixture(self, resolve):
        @provide(spec=1)
        @provide(spec=2)
        @provide()
        def fn():
            pass

        fn()

        self.assertEqual(resolve.mock_calls, [call(1), call(2), call(1)])

    @patch("protestr.resolve")
    def test_provide_should_tear_down(self, resolve):
        class Resource:
            def __init__(self):
                self.torndown = False

            def __teardown__(self):
                self.torndown = True

        @provide([Resource] * 2)
        def fn():
            raise Exception("failure")

        expected_resources = {
            "resources": [
                r1 := Resource(),
                r2 := Resource(),
            ]
        }

        resolve.return_value = expected_resources

        try:
            fn()
        except Exception as e:
            (message,) = e.args
            self.assertEqual(message, "failure")

        self.assertTrue(r1.torndown)
        self.assertTrue(r2.torndown)

    @patch("protestr.resolve")
    def test_provide_should_allow_overriding_specs(self, resolve):
        @provide(x=0)
        @provide(x=1)
        def fn(x):
            pass

        fn()
        fn(x=2)

        self.assertEqual(resolve.mock_calls, [call(0), call(1), call(2), call(2)])

    @patch("protestr.resolve")
    def test_provide_should_not_resolve_other_params(self, resolve):
        @provide(x=0)
        @provide(x=1)
        def fn(x, y=2):
            pass

        fn()
        fn(y=2)

        self.assertEqual(resolve.mock_calls, [call(0), call(1), call(0), call(1)])


if __name__ == "__main__":
    unittest.main()
