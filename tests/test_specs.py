import unittest
from unittest.mock import MagicMock, patch, call
from protestr import provide
from protestr.specs import between, choice, sample, choices, recipe
import random


class TestSpecs(unittest.TestCase):
    @provide(m=int, n=int)
    @patch("protestr._specs.resolve")
    def test_between_ints(self, resolve, m, n):
        resolve.side_effect = [m, n]

        intgr = between(int, int)()

        self.assertEqual(resolve.mock_calls, [call(int), call(int)])
        self.assertIsInstance(intgr, int)
        self.assertTrue(min(m, n) <= intgr <= max(m, n))

    @provide(m=float, n=float)
    @patch("protestr._specs.resolve")
    def test_between_floats(self, resolve, m, n):
        resolve.side_effect = [m, n]

        real = between(float, float)()

        self.assertEqual(resolve.mock_calls, [call(float), call(float)])
        self.assertIsInstance(real, float)
        self.assertTrue(min(m, n) <= real <= max(m, n))

    @provide(m=int, n=float)
    @patch("protestr._specs.resolve")
    def test_between_int_float(self, resolve, m, n):
        resolve.side_effect = [m, n]

        real = between(int, float)()

        self.assertEqual(resolve.mock_calls, [call(int), call(float)])
        self.assertIsInstance(real, float)
        self.assertTrue(min(m, n) <= real <= max(m, n))

    @provide(m=float, n=int)
    @patch("protestr._specs.resolve")
    def test_between_float_int(self, resolve, m, n):
        resolve.side_effect = [m, n]

        real = between(float, int)()

        self.assertEqual(resolve.mock_calls, [call(float), call(int)])
        self.assertIsInstance(real, float)
        self.assertTrue(min(m, n) <= real <= max(m, n))

    @provide(elems=3 * [int])
    @patch("protestr._specs.resolve")
    def test_choice_from_collection(self, resolve, elems):
        elems_spec = 3 * [int]
        resolve.return_value = elems

        intgr = choice(elems_spec)()

        resolve.assert_called_once_with(elems_spec)
        self.assertIn(intgr, elems)

    @provide(elems=[int] * 3)
    @patch("protestr._specs.resolve")
    def test_choice_from_args(self, resolve, elems):
        elems_spec = (int,) * 3
        resolve.return_value = elems

        intgr = choice(*elems_spec)()

        resolve.assert_called_once_with(elems_spec)
        self.assertIn(intgr, elems)

    @provide(all_elems=3 * (int,))
    @patch("protestr._specs.randsample")
    @patch("protestr._specs.resolve")
    def test_sample_of_k_from_args(self, resolve, randsample, all_elems):
        filt_elems = random.sample(all_elems, 2)
        all_elems_spec = 3 * (int,)
        k_spec = between(1, 2)

        resolve.side_effect = [all_elems, 2]

        randsample.return_value = filt_elems

        self.assertEqual(sample(*all_elems_spec, k=k_spec)(), (*filt_elems,))

        self.assertEqual(resolve.mock_calls, [call(all_elems_spec), call(k_spec)])

        randsample.assert_called_once_with(population=all_elems, k=2)

    @provide(all_elems=3 * (int,))
    @patch("protestr._specs.randsample")
    @patch("protestr._specs.resolve")
    def test_sample_of_k_from_tuple(self, resolve, randsample, all_elems):
        filt_elems = random.sample(all_elems, 2)
        all_elems_spec = 3 * (int,)
        k_spec = between(1, 2)

        resolve.side_effect = [all_elems, 2]

        randsample.return_value = filt_elems

        self.assertEqual(sample(all_elems_spec, k=k_spec)(), (*filt_elems,))

        self.assertEqual(resolve.mock_calls, [call(all_elems_spec), call(k_spec)])

        randsample.assert_called_once_with(population=all_elems, k=2)

    @provide(all_elems=3 * [int])
    @patch("protestr._specs.randsample")
    @patch("protestr._specs.resolve")
    def test_sample_of_k_from_list(self, resolve, randsample, all_elems):
        filt_elems = random.sample(all_elems, 2)
        all_elems_spec = 3 * [int]
        k_spec = between(1, 2)

        resolve.side_effect = [all_elems, 2]

        randsample.return_value = filt_elems

        self.assertEqual(sample(all_elems_spec, k=k_spec)(), filt_elems)

        self.assertEqual(resolve.mock_calls, [call(all_elems_spec), call(k_spec)])

        randsample.assert_called_once_with(population=all_elems, k=2)

    @provide(full_str=str)
    @patch("protestr._specs.randsample")
    @patch("protestr._specs.resolve")
    def test_sample_of_k_from_str(self, resolve, randsample, full_str):
        if len(full_str) < 3:
            full_str *= 3

        filt_chars = random.sample(full_str, 2)
        k_spec = between(1, 2)

        resolve.side_effect = [full_str, 2]

        randsample.return_value = filt_chars

        self.assertEqual(sample(str, k=k_spec)(), "".join(filt_chars))

        self.assertEqual(resolve.mock_calls, [call(str), call(k_spec)])

        randsample.assert_called_once_with(population=full_str, k=2)

    @provide(all_elems=3 * (int,))
    @patch("protestr._specs.randchoices")
    @patch("protestr._specs.resolve")
    def test_choices_of_k_from_args(self, resolve, randchoices, all_elems):
        chosen_elems = random.choices(all_elems, k=2)
        all_elems_spec = 3 * (int,)
        k_spec = between(1, 2)

        resolve.side_effect = [all_elems, 2]

        randchoices.return_value = chosen_elems

        self.assertEqual(choices(*all_elems_spec, k=k_spec)(), (*chosen_elems,))

        self.assertEqual(resolve.mock_calls, [call(all_elems_spec), call(k_spec)])

        randchoices.assert_called_once_with(population=all_elems, k=2)

    @provide(all_elems=3 * (int,))
    @patch("protestr._specs.randchoices")
    @patch("protestr._specs.resolve")
    def test_choices_of_k_from_tuple(self, resolve, randchoices, all_elems):
        chosen_elems = random.choices(all_elems, k=2)
        all_elems_spec = 3 * (int,)
        k_spec = between(1, 2)

        resolve.side_effect = [all_elems, 2]

        randchoices.return_value = chosen_elems

        self.assertEqual(choices(all_elems_spec, k=k_spec)(), (*chosen_elems,))

        self.assertEqual(resolve.mock_calls, [call(all_elems_spec), call(k_spec)])

        randchoices.assert_called_once_with(population=all_elems, k=2)

    @provide(all_elems=3 * [int])
    @patch("protestr._specs.randchoices")
    @patch("protestr._specs.resolve")
    def test_choices_of_k_from_list(self, resolve, randchoices, all_elems):
        chosen_elems = random.choices(all_elems, k=2)
        all_elems_spec = 3 * [int]
        k_spec = between(1, 2)

        resolve.side_effect = [all_elems, 2]

        randchoices.return_value = chosen_elems

        self.assertEqual(choices(all_elems_spec, k=k_spec)(), chosen_elems)

        self.assertEqual(resolve.mock_calls, [call(all_elems_spec), call(k_spec)])

        randchoices.assert_called_once_with(population=all_elems, k=2)

    @provide(full_str=str)
    @patch("protestr._specs.randchoices")
    @patch("protestr._specs.resolve")
    def test_choices_of_k_from_str(self, resolve, randchoices, full_str):
        if len(full_str) < 3:
            full_str *= 3

        chosen_chars = random.choices(full_str, k=2)
        k_spec = between(1, 2)

        resolve.side_effect = [full_str, 2]

        randchoices.return_value = chosen_chars

        self.assertEqual(choices(str, k=k_spec)(), "".join(chosen_chars))

        self.assertEqual(resolve.mock_calls, [call(str), call(k_spec)])

        randchoices.assert_called_once_with(population=full_str, k=2)

    @provide(elems=3 * [int], result=str)
    @patch("protestr._specs.resolve")
    def test_recipe_from_collection(self, resolve, elems, result):
        elems_specs = 3 * [int]
        resolve.return_value = elems
        then = MagicMock(return_value=result)

        self.assertEqual(recipe(elems_specs, then=then)(), result)

        resolve.assert_called_once_with(elems_specs)
        then.assert_called_once_with(elems)

    @provide(elems=3 * (int,), result=str)
    @patch("protestr._specs.resolve")
    def test_recipe_from_args(self, resolve, elems, result):
        elems_specs = 3 * (int,)
        resolve.return_value = elems
        then = MagicMock(return_value=result)

        self.assertEqual(recipe(*elems_specs, then=then)(), result)

        resolve.assert_called_once_with(elems_specs)
        then.assert_called_once_with(elems)


if __name__ == "__main__":
    unittest.main()
