import unittest
from unittest.mock import patch, call
from protestr import provide


class Tearable:
    def __init__(self):
        self.torndown = False

    def __teardown__(self):
        self.torndown = True


class TestProvider(unittest.TestCase):
    @patch("protestr.resolve")
    def test_provide_once(self, resolve):
        resolve.side_effect = lambda s: s() if callable(s) else s

        def orig_func(*args, **kwds): return args, kwds

        provided_func = provide(
            tearable=Tearable,
            provided_kwd="provided_kwd",
            orig_func_kwd="modified_func_kwd"
        )(orig_func)

        (arg,), kwds = provided_func(
            "orig_func_arg",
            orig_func_kwd="orig_func_kwd"
        )

        self.assertEqual(arg, "orig_func_arg")

        self.assertIsInstance(kwds, dict)

        self.assertEqual(
            [*kwds], [
                "tearable",
                "provided_kwd",
                "orig_func_kwd"
            ]
        )

        self.assertEqual(kwds["orig_func_kwd"], "orig_func_kwd")
        self.assertEqual(kwds["provided_kwd"], "provided_kwd")
        self.assertTrue(kwds["tearable"].torndown)

        self.assertEqual(
            resolve.mock_calls, [
                call(Tearable),
                call("provided_kwd"),
                call("orig_func_kwd")
            ]
        )

    @patch("protestr.resolve")
    def test_provide_once_tearable_collection(self, resolve):
        resolve.side_effect = [[Tearable()]]

        def orig_func(tearables): return tearables

        provided_func = provide(tearables=[Tearable])(orig_func)

        tearable, = provided_func()

        self.assertTrue(tearable.torndown)

    @patch("protestr.resolve")
    def test_provide_thrice(self, resolve):
        resolve.side_effect = lambda s: s() if callable(s) else s

        def orig_func(*args, **kwds): return args, kwds

        provided_func = provide(
            tearable=Tearable,
            provided_kwd="provided_kwd1",
            orig_func_kwd="modified_func_kwd1"
        )(orig_func)

        provided_func = provide(
            tearable=Tearable,
            provided_kwd="provided_kwd2",
            orig_func_kwd="modified_func_kwd2"
        )(provided_func)

        provided_func = provide(
            tearable=Tearable,
            provided_kwd="provided_kwd3",
            orig_func_kwd="modified_func_kwd3"
        )(provided_func)

        (arg,), kwds = provided_func(
            "orig_func_arg",
            orig_func_kwd="orig_func_kwd"
        )

        self.assertEqual(arg, "orig_func_arg")

        self.assertIsInstance(kwds, dict)

        self.assertEqual(
            [*kwds], [
                "tearable",
                "provided_kwd",
                "orig_func_kwd"
            ]
        )

        self.assertEqual(kwds["orig_func_kwd"], "orig_func_kwd")
        self.assertEqual(kwds["provided_kwd"], "provided_kwd3")
        self.assertTrue(kwds["tearable"].torndown)

        self.assertEqual(
            resolve.mock_calls, [
                call(Tearable),
                call("provided_kwd1"),
                call("orig_func_kwd"),
                call(Tearable),
                call("provided_kwd2"),
                call("orig_func_kwd"),
                call(Tearable),
                call("provided_kwd3"),
                call("orig_func_kwd")
            ]
        )

    @patch("protestr.resolve")
    def test_provide_thrice_tearable_collection(self, resolve):
        tearable1 = Tearable()
        tearable2 = Tearable()
        tearable3 = Tearable()

        resolve.side_effect = [[tearable1], [tearable2], [tearable3]]

        def orig_func(tearables): return tearables

        provided_func = provide(tearables=[Tearable])(orig_func)
        provided_func = provide(tearables=[Tearable])(provided_func)
        provided_func = provide(tearables=[Tearable])(provided_func)

        tearable, = provided_func()
        self.assertEqual(tearable, tearable3)

        self.assertTrue(tearable1.torndown)
        self.assertTrue(tearable2.torndown)
        self.assertTrue(tearable3.torndown)


if __name__ == "__main__":
    unittest.main()
