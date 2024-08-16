import unittest
from unittest.mock import MagicMock, patch, call
from protestr import provide


class Tearable:
    _trdown_attmpt = 0

    def __init__(self, name="", raises=False):
        self.name = name
        self.raises = raises
        self.torndown = False
        self.trdown_attmpt = None

    def __teardown__(self):
        Tearable._trdown_attmpt += 1
        self.trdown_attmpt = Tearable._trdown_attmpt
        if self.raises:
            raise Exception(f"{self.name} failed")
        self.torndown = True


class TestProvider(unittest.TestCase):
    @patch("protestr.resolve")
    def test_provide_for_passing_teardowns(self, resolve):
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
    def test_provide_for_failing_teardowns(self, resolve):
        resolve.side_effect = lambda s: s
        orig_func = MagicMock()
        bad_tearable1 = Tearable(name="bad tearable 1", raises=True)
        bad_tearable2 = Tearable(name="bad tearable 2", raises=True)
        good_tearable = Tearable()

        try:
            provided_func = provide(
                arg1=bad_tearable1,
                arg2="to override later when provided_func is called",
                arg3=good_tearable
            )(orig_func)

            provided_func(arg2=bad_tearable2)
        except Exception as ex:
            inr_ex1, inr_ex2 = ex.args

        self.assertEqual(
            resolve.mock_calls, [
                call(bad_tearable1),
                call(bad_tearable2),
                call(good_tearable)
            ]
        )

        orig_func.assert_called_once_with(
            arg1=bad_tearable1,
            arg2=bad_tearable2,
            arg3=good_tearable
        )

        self.assertIsInstance(inr_ex1, Exception)
        message1, = inr_ex1.args
        self.assertEqual(message1, f"{bad_tearable1.name} failed")

        self.assertIsInstance(inr_ex2, Exception)
        message2, = inr_ex2.args
        self.assertEqual(message1, f"{bad_tearable1.name} failed")

        self.assertEqual(bad_tearable1.trdown_attmpt, 1)
        self.assertEqual(bad_tearable2.trdown_attmpt, 2)
        self.assertEqual(good_tearable.trdown_attmpt, 3)

        self.assertFalse(bad_tearable1.torndown)
        self.assertFalse(bad_tearable2.torndown)
        self.assertTrue(good_tearable.torndown)

    @patch("protestr.resolve")
    def test_provide_for_tearable_collections(self, resolve):
        tearable = Tearable()

        resolve.side_effect = [[tearable]]

        def orig_func(tearables): return tearables

        provided_func = provide(tearables=[Tearable])(orig_func)

        tearable, = provided_func()

        self.assertTrue(tearable.torndown)


if __name__ == "__main__":
    unittest.main()
