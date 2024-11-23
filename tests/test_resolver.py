import unittest
from unittest.mock import MagicMock, patch, call
from string import ascii_letters
from protestr import provide, resolve
from protestr.specs import between, choice, choices


class TestResolver(unittest.TestCase):
    @provide(x=between(0, 1000))
    @patch("protestr._resolver.randint")
    def test_resolve_should_generate_int(self, randint, x):
        randint.return_value = x

        self.assertEqual(resolve(int), x)

        randint.assert_called_once_with(0, 1000)

    @provide(x=between(0.0, 1000))
    @patch("protestr._resolver.uniform")
    def test_resolve_should_generate_float(self, uniform, x):
        uniform.return_value = x

        self.assertEqual(resolve(float), x)

        uniform.assert_called_once_with(0, 1000)

    @provide(x=between(-1000.0, 1000), y=between(-1000.0, 1000))
    @patch("protestr._resolver.uniform")
    def test_resolve_should_generate_complex(self, uniform, x, y):
        uniform.side_effect = [x, y]

        self.assertEqual(resolve(complex), complex(x, y))

        self.assertEqual(uniform.mock_calls, [call(-1000, 1000), call(-1000, 1000)])

    @provide(x=choice(True, False))
    @patch("protestr._resolver.randchoice")
    def test_resolve_should_generate_bool(self, randchoice, x):
        randchoice.return_value = x

        self.assertEqual(resolve(bool), x)

        randchoice.assert_called_once_with((True, False))

    @provide(x=choices(ascii_letters, k=len(ascii_letters)), k=int)
    @patch("protestr._resolver.randint")
    @patch("protestr._resolver.randchoices")
    def test_resolve_should_generate_str(self, randchoices, randint, x, k):
        randchoices.return_value = [*x]
        randint.return_value = k

        self.assertEqual(resolve(str), "".join(x))

        randchoices.assert_called_once_with(ascii_letters, k=k)
        randint.assert_called_once_with(1, 50)

    @provide(n=between(1, 10), x=int)
    def test_resolve_should_resolve_tuple(self, n, x):
        spec = (between(x, x),) * n
        self.assertEqual(resolve(spec), (x,) * n)

    @provide(n=between(1, 10), x=int)
    def test_resolve_list(self, n, x):
        spec = [between(x, x)] * n
        self.assertEqual(resolve(spec), [x] * n)

    @provide(x=int)
    def test_resolve_should_resolve_set(self, x):
        spec = {between(x, x), between(x + 1, x + 1), between(x + 2, x + 2)}
        self.assertEqual(resolve(spec), {x, x + 1, x + 2})

    @provide(key=int, val=int)
    def test_resolve_should_resolve_dict(self, key, val):
        spec = {between(key, key): between(val, val)}
        self.assertEqual(resolve(spec), {key: val})

    @provide(x=int)
    def test_resolve_should_call_callable(self, x):
        fn = MagicMock(return_value=x)
        self.assertEqual(resolve(fn), x)

    @provide(x=int)
    def test_resolve_should_resolve_indefinitely(self, x):
        inner = MagicMock(return_value=x)
        outer = MagicMock(return_value=inner)

        self.assertEqual(resolve(outer), x)

        outer.assert_called_once()
        inner.assert_called_once()


if __name__ == "__main__":
    unittest.main()
