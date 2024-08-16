import unittest
from unittest.mock import MagicMock, patch, call
from protestr import provide
from protestr.specs import (
    between, single, combination, permutation, merged
)
import random


class TestSpecs(unittest.TestCase):
    @provide(m=int, n=int)
    @patch("protestr._specs.resolve")
    def test_between_ints(self, resolve, m, n):
        resolve.side_effect = (m, n)

        intgr = between(int, int)()

        self.assertEqual(resolve.mock_calls, [call(int), call(int)])
        self.assertIsInstance(intgr, int)
        self.assertTrue(min(m, n) <= intgr <= max(m, n))

    @provide(m=float, n=float)
    @patch("protestr._specs.resolve")
    def test_between_floats(self, resolve, m, n):
        resolve.side_effect = (m, n)

        real = between(float, float)()

        self.assertEqual(resolve.mock_calls, [call(float), call(float)])
        self.assertIsInstance(real, float)
        self.assertTrue(min(m, n) <= real <= max(m, n))

    @provide(m=int, n=float)
    @patch("protestr._specs.resolve")
    def test_between_int_float(self, resolve, m, n):
        resolve.side_effect = (m, n)

        real = between(int, float)()

        self.assertEqual(resolve.mock_calls, [call(int), call(float)])
        self.assertIsInstance(real, float)
        self.assertTrue(min(m, n) <= real <= max(m, n))

    @provide(m=float, n=int)
    @patch("protestr._specs.resolve")
    def test_between_float_int(self, resolve, m, n):
        resolve.side_effect = (m, n)

        real = between(float, int)()

        self.assertEqual(resolve.mock_calls, [call(float), call(int)])
        self.assertIsInstance(real, float)
        self.assertTrue(min(m, n) <= real <= max(m, n))

    @provide(elems=3*[int])
    @patch("protestr._specs.resolve")
    def test_single_from_collection(self, resolve, elems):
        elems_spec = 3 * [int]
        resolve.side_effect = [elems]

        intgr = single(elems_spec)()

        resolve.assert_called_once_with(elems_spec)
        self.assertIn(intgr, elems)

    @provide(elems=[int]*3)
    @patch("protestr._specs.resolve")
    def test_single_from_args(self, resolve, elems):
        elems_spec = (int,) * 3
        resolve.side_effect = [elems]

        intgr = single(*elems_spec)()

        resolve.assert_called_once_with(elems_spec)
        self.assertIn(intgr, elems)

    @provide(all_elems=3*(int,))
    @patch("protestr._specs.sample")
    @patch("protestr._specs.resolve")
    def test_combination_of_k_from_args(
        self, resolve, sample, all_elems
    ):
        filt_elems = random.sample(all_elems, 2)
        all_elems_spec = 3 * (int,)
        k_spec = between(1, 2)

        resolve.side_effect = [all_elems, 2]

        sample.side_effect = [filt_elems]

        self.assertEqual(
            combination(*all_elems_spec, k=k_spec)(),
            (*filt_elems,)
        )

        self.assertEqual(
            resolve.mock_calls, [
                call(all_elems_spec), call(k_spec)
            ]
        )

        sample.assert_called_once_with(population=all_elems, k=2)

    @provide(all_elems=3*(int,))
    @patch("protestr._specs.sample")
    @patch("protestr._specs.resolve")
    def test_combination_of_k_from_tuple(
        self, resolve, sample, all_elems
    ):
        filt_elems = random.sample(all_elems, 2)
        all_elems_spec = 3 * (int,)
        k_spec = between(1, 2)

        resolve.side_effect = [all_elems, 2]

        sample.side_effect = [filt_elems]

        self.assertEqual(
            combination(all_elems_spec, k=k_spec)(),
            (*filt_elems,)
        )

        self.assertEqual(
            resolve.mock_calls, [
                call(all_elems_spec), call(k_spec)
            ]
        )

        sample.assert_called_once_with(population=all_elems, k=2)

    @provide(all_elems=3*[int])
    @patch("protestr._specs.sample")
    @patch("protestr._specs.resolve")
    def test_combination_of_k_from_list(
        self, resolve, sample, all_elems
    ):
        filt_elems = random.sample(all_elems, 2)
        all_elems_spec = 3 * [int]
        k_spec = between(1, 2)

        resolve.side_effect = [all_elems, 2]

        sample.side_effect = [filt_elems]

        self.assertEqual(
            combination(all_elems_spec, k=k_spec)(),
            filt_elems
        )

        self.assertEqual(
            resolve.mock_calls, [
                call(all_elems_spec), call(k_spec)
            ]
        )

        sample.assert_called_once_with(population=all_elems, k=2)

    @provide(full_str=str)
    @patch("protestr._specs.sample")
    @patch("protestr._specs.resolve")
    def test_combination_of_k_from_str(
        self, resolve, sample, full_str
    ):
        if len(full_str) < 3:
            full_str *= 3

        filt_chars = random.sample(full_str, 2)
        k_spec = between(1, 2)

        resolve.side_effect = [full_str, 2]

        sample.side_effect = [filt_chars]

        self.assertEqual(
            combination(str, k=k_spec)(),
            "".join(filt_chars)
        )

        self.assertEqual(
            resolve.mock_calls, [
                call(str), call(k_spec)
            ]
        )

        sample.assert_called_once_with(population=full_str, k=2)

    @provide(all_elems=3*(int,))
    @patch("protestr._specs.choices")
    @patch("protestr._specs.resolve")
    def test_permutation_of_k_from_args(
        self, resolve, choices, all_elems
    ):
        chosen_elems = random.choices(all_elems, k=2)
        all_elems_spec = 3 * (int,)
        k_spec = between(1, 2)

        resolve.side_effect = [all_elems, 2]

        choices.side_effect = [chosen_elems]

        self.assertEqual(
            permutation(*all_elems_spec, k=k_spec)(),
            (*chosen_elems,)
        )

        self.assertEqual(
            resolve.mock_calls, [
                call(all_elems_spec), call(k_spec)
            ]
        )

        choices.assert_called_once_with(population=all_elems, k=2)

    @provide(all_elems=3*(int,))
    @patch("protestr._specs.choices")
    @patch("protestr._specs.resolve")
    def test_permutation_of_k_from_tuple(
        self, resolve, choices, all_elems
    ):
        chosen_elems = random.choices(all_elems, k=2)
        all_elems_spec = 3 * (int,)
        k_spec = between(1, 2)

        resolve.side_effect = [all_elems, 2]

        choices.side_effect = [chosen_elems]

        self.assertEqual(
            permutation(all_elems_spec, k=k_spec)(),
            (*chosen_elems,)
        )

        self.assertEqual(
            resolve.mock_calls, [
                call(all_elems_spec), call(k_spec)
            ]
        )

        choices.assert_called_once_with(population=all_elems, k=2)

    @provide(all_elems=3*[int])
    @patch("protestr._specs.choices")
    @patch("protestr._specs.resolve")
    def test_permutation_of_k_from_list(
        self, resolve, choices, all_elems
    ):
        chosen_elems = random.choices(all_elems, k=2)
        all_elems_spec = 3 * [int]
        k_spec = between(1, 2)

        resolve.side_effect = [all_elems, 2]

        choices.side_effect = [chosen_elems]

        self.assertEqual(
            permutation(all_elems_spec, k=k_spec)(),
            chosen_elems
        )

        self.assertEqual(
            resolve.mock_calls, [
                call(all_elems_spec), call(k_spec)
            ]
        )

        choices.assert_called_once_with(population=all_elems, k=2)

    @provide(full_str=str)
    @patch("protestr._specs.choices")
    @patch("protestr._specs.resolve")
    def test_permutation_of_k_from_str(
        self, resolve, choices, full_str
    ):
        if len(full_str) < 3:
            full_str *= 3

        chosen_chars = random.choices(full_str, k=2)
        k_spec = between(1, 2)

        resolve.side_effect = [full_str, 2]

        choices.side_effect = [chosen_chars]

        self.assertEqual(
            permutation(str, k=k_spec)(),
            "".join(chosen_chars)
        )

        self.assertEqual(
            resolve.mock_calls, [
                call(str), call(k_spec)
            ]
        )

        choices.assert_called_once_with(population=full_str, k=2)

    @provide(elems=3*[int], mergefunc=MagicMock, merge_result=int)
    @patch("protestr._specs.resolve")
    def test_merged_from_collection(
        self, resolve, elems, mergefunc, merge_result
    ):
        resolve.side_effect = [elems]
        mergefunc.side_effect = [merge_result]
        specs = 3 * [int]

        self.assertEqual(merged(specs, func=mergefunc)(), merge_result)

        resolve.assert_called_once_with(specs)
        mergefunc.assert_called_once_with(elems)

    @provide(elems=3*[int], mergefunc=MagicMock, merge_result=int)
    @patch("protestr._specs.resolve")
    def test_merged_from_args(
        self, resolve, elems, mergefunc, merge_result
    ):
        resolve.side_effect = [elems]
        mergefunc.side_effect = [merge_result]
        specs = 3 * (int,)

        self.assertEqual(merged(*specs, func=mergefunc)(), merge_result)

        resolve.assert_called_once_with(specs)
        mergefunc.assert_called_once_with(elems)


if __name__ == "__main__":
    unittest.main()
