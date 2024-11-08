import unittest
from unittest.mock import Mock, patch, call
from string import ascii_letters
from protestr import provide, resolve
from protestr.specs import between, choice, choices


class TestResolver(unittest.TestCase):
    @provide(x=between(0, 1000))
    @patch("protestr._resolver.randint")
    def test_resolve_int(self, randint, x):
        randint.return_value = x

        self.assertEqual(resolve(int), x)

        randint.assert_called_once_with(0, 1000)

    @provide(x=between(0.0, 1000))
    @patch("protestr._resolver.uniform")
    def test_resolve_float(self, uniform, x):
        uniform.return_value = x

        self.assertEqual(resolve(float), x)

        uniform.assert_called_once_with(0, 1000)

    @provide(x=between(-1000.0, 1000), y=between(-1000.0, 1000))
    @patch("protestr._resolver.uniform")
    def test_resolve_complex(self, uniform, x, y):
        uniform.side_effect = [x, y]

        self.assertEqual(resolve(complex), complex(x, y))

        self.assertEqual(uniform.mock_calls, [call(-1000, 1000), call(-1000, 1000)])

    @provide(x=choice(True, False))
    @patch("protestr._resolver.randchoice")
    def test_resolve_bool(self, randchoice, x):
        randchoice.return_value = x

        self.assertEqual(resolve(bool), x)

        randchoice.assert_called_once_with((True, False))

    @provide(x=choices(ascii_letters, k=len(ascii_letters)), k=int)
    @patch("protestr._resolver.randint")
    @patch("protestr._resolver.randchoices")
    def test_resolve_str(self, randchoices, randint, x, k):
        randchoices.return_value = [*x]
        randint.return_value = k

        self.assertEqual(resolve(str), "".join(x))

        randchoices.assert_called_once_with(ascii_letters, k=k)
        randint.assert_called_once_with(1, 50)

    @provide(n=between(1, 10), x=int)
    def test_resolve_tuple(self, n, x):
        self.assertEqual(resolve(n * tuple([between(x, x)])), n * (x,))

    @provide(n=between(1, 10), x=int)
    def test_resolve_list(self, n, x):
        self.assertEqual(resolve(n * [between(x, x)]), n * [x])

    @provide(x=int)
    def test_resolve_set(self, x):
        self.assertEqual(
            resolve({between(x, x), between(x + 1, x + 1), between(x + 2, x + 2)}),
            {x, x + 1, x + 2},
        )

    @provide(key=int, val=int)
    def test_resolve_dict(self, key, val):
        self.assertEqual(resolve({between(key, key): between(val, val)}), {key: val})

    @provide(x=int)
    def test_resolve_callable(self, x):
        inner = Mock(return_value=x)
        outer = Mock(return_value=inner)

        self.assertEqual(resolve(outer), x)

        outer.assert_called_once()
        inner.assert_called_once()


if __name__ == "__main__":
    unittest.main()
