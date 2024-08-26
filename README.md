# protestr

[![PyPI - Version](https://img.shields.io/pypi/v/protestr.svg)](https://pypi.org/project/protestr)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/protestr.svg)](https://pypi.org/project/protestr)

-----

Test like a pro with Protestr — the state-of-the-art test fixture
configurator for Python, written in Python, tested with Protestr itself!

## Table of Contents

1. [TL;DR](#tldr)
1. [Rationale](#rationale)
1. [Getting Started](#getting-started)
   1. [Installation](#installation)
   1. [Defining Specs](#defining-specs)
   1. [Ensuring Teardown](#ensuring-teardown)
1. [Documentation](#documentation)
1. [Working Example](#working-example)
1. [License](#license)

## TL;DR

```python
class TestFactorial(unittest.TestCase):
    @provide(n=9, expected=362880)
    @provide(n=5, expected=120)
    @provide(n=1, expected=1)
    @provide(n=0, expected=1)
    def test_factorial_valid_number(self, n, expected):
        self.assertEqual(factorial(n), expected)

    @provide(n=1.5, expected="n must be an integer")
    @provide(n=between(-10000, -1), expected="n must be non-negative")
    def test_factorial_invalid_number(self, n, expected):
        try:
            factorial(n)
        except Exception as e:
            message, = e.args

        self.assertEqual(message, expected)
```

Find more sophisticated usages in the
[Working Example](#working-example).

## Rationale

A test fixture is any arrangement necessary for running tests,
consisting of dummies, mocks, stubs, fakes, and even concrete
implementations. A well-configured fixture leads to a consistent and
reliable testing environment in contrast to an ill-configured one, which
is a growing maintenance burden. Good fixtures can support multiple
tests with modifications, such as a database seeded differently each
time to test a different operation like insertion or deletion. They are
also responsible for ensuring the proper disposal of resources without a
miss, especially across multiple tests and files. Their configuration
logic does not hijack focus from acts and assertions, and they are
always reusable with all necessary adjustments. That's where Protestr
comes in. It offers a declarative syntax for fixture customization to
make tests concise, expressive, and reusable like never before.

## Getting Started

### Installation

Protestr is available as
[`protestr`](https://pypi.org/project/protestr/) on PyPI and can be
installed with:

```shell
pip install protestr
```

### Defining Specs

A fixture is technically a set of specifications (specs) "provided" to a
function to resolve into actual data. The specs — usually functions —
describe how different parts of the fixture form. Protestr offers a few
built-in specs in `protestr.specs`, but you may need more. So, let's
define an example geo-coordinate spec to start with. A valid
geo-coordinate consists of a latitude between [-90, 90], a longitude
between [-180, 180], and an altitude — something like:

```python
from protestr import provide
from protestr.specs import between

@provide(
    lat=between(-90.0, 90.0),
    lon=between(-180.0, 180.0),
    alt=float
)
def geo_coord(lat, lon, alt):
    return lat, lon, alt
```

Thus, we have our first spec — `geo_coord`. Intuitive, isn't it? Now, we
can "resolve" (generate) geo-coordinates whenever we need to in the
following ways:

1. Call without args:

   ```pycon
   >>> geo_coord()
   (-28.56218898364334, 74.83481448106508, 103.16808817617861)
   ```

   Why invent args when Protestr can provide them?

1. Call with overridden specs:

   ```pycon
   >>> geo_coord(
   ...     lat=choice("equator", "north pole", "south pole"),
   ...     alt=int
   ... )
   ('north pole', -107.37336459941672, 581)
   ```

   Here, `lat` and `alt` have been overridden by passing `choice()` (a
   built-in spec) and `int`. We can also pass specs composed of other
   specs:

   ```pycon
   >>> geo_coord(
   ...     lat=choice(
   ...         choice("north pole", "south pole"),
   ...         choice("arctic circle", "antarctic circle")
   ...     )
   ... )
   ('arctic circle', 79.02746924451344, 489.26084905383436)
   ```

   So, we're asking it to choose one from "north pole" and "south pole",
   then one from "arctic circle" and "antarctic circle", and finally one
   from both results.

   **Passing specs around in this manner works as long as they are
   passed intact.**

   To clarify, here's an example of an incorrect approach:

   ```pycon
   >>> geo_coord(
   ...     lat=choice(
   ...         str(choice("north pole", "south pole")).upper(), # ❌
   ...         choice("arctic circle", "antarctic circle")
   ...     )
   ... )
   ('<FUNCTION CHOICE.<LOCALS>.<LAMBDA> AT 0X000002AC8D9A2B00>', -72.90254553301114, 444.88184046168556)
   ```

   Here, `choice()` (a spec) got consumed by `str` before being passed
   to `lat` in `geo_coord` (so it wasn't intact). The correct approach:

   ```python
   >>> geo_coord(
   ...     lat=choice(
   ...         recipe(
   ...             choice("north pole", "south pole"), ✅
   ...             then=str.upper
   ...         ),
   ...         choice("arctic circle", "antarctic circle")
   ...     )
   ... )
   ('NORTH POLE', 6.952083290868416, 186.75647508172466)
   ```

1. Resolve with `resolve`:

   ```
   >>> from protestr import resolve
   >>> resolve(geo_coord)
   (-68.79360870922969, 8.200171266070214, 691.5305890425291)

   >>> resolve(2*[geo_coord])
   [(41.98113033422453, 24.72261644345585, 115.79597793585394),
    (84.72658072806291, 84.71585789666494, 731.1552031682041)]
   ```

   `resolve` also works with other types, as mentioned in the
   [Documentation](#documentation).

1. Provide with `provide()`:

   ```python
   @provide(two_coords=2*[geo_coord])
   def line(two_coords):
       start, end = two_coords
       return start, end
   ```

   `provide()` is the decorator version of `resolve` that accepts
   multiple specs as keyword args and provides them to a function.

> [!NOTE]
> The `provide()` decorator works seamlessly when used alongside other
> decorators, such as Python's handy `patch()` decorator. Please note,
> however, that the `patch()` decorators must be next to one another,
> and in the list of parameters, they must appear in the reverse order
> as in the list of decorators (bottom-up). That's how `patch()` works
> (more info in
> [unittest.mock - Quick Guide](https://docs.python.org/3/library/unittest.mock.html#quick-guide)).
>
> ```pycon
> >>> from unittest.mock import patch
> >>> from protestr import provide
>
> >>> @provide(intgr=int)
> ... @patch('module.ClassName2')
> ... @patch('module.ClassName1')
> ... def test(MockClass1, MockClass2, intgr):
> ...     module.ClassName1()
> ...     module.ClassName2()
> ...     assert MockClass1 is module.ClassName1
> ...     assert MockClass2 is module.ClassName2
> ...     assert MockClass1.called
> ...     assert MockClass2.called
> ...     assert isinstance(intgr, int)
> ...
> >>> test()
> ```

### Ensuring Teardown

Good fixture design demands remembering to dispose of resources at the
end of tests. Protestr takes care of it out of the box with the
`__teardown__` function. Whenever a `provide()`-applied function returns
or terminates abnormally, it looks for `__teardown__` in each (resolved)
object it provided and invokes it on the object if found. So, all you
need to do is define `__teardown__` once in a class, and it will be
called every time you provide one.

```python
class UsersDB:
    def __init__(self, users):
        self.users = users

    def insert(self, user):
        self.users.append(user)

    def __teardown__(self):
        self.users = []
```

## Documentation

$\large \color{gray}@protestr.\color{black}\textbf{provide(**specs)}$

Provide resolved specs to a function.

The specs are provided implicitly from keyword args in `provide()` to
the matching parameters of the function when called with those args
omitted. When specified as keyword args, they override the original
specs.

```python
@provide(
    uppercase=choice(ascii_uppercase),
    lowercase=choice(ascii_lowercase),
    digit=choice(digits),
    chars=choices(str, k=between(5, 100))
)
def password(uppercase, lowercase, digit, chars):
    return "".join((uppercase, lowercase, digit, chars))

@provide(
    password=password,
    username=choices(ascii_lowercase, k=between(4, 12))
)
def credentials(username, password):
    return username, password
```
```pycon
>>> credentials()
('cgbqkmsehf', 'Pr8LOipCBKCBkAxbbKykppKkALxykKLOiKpiy')
```
```pycon
>>> credentials(username="johndoe")
('johndoe', 'En2HivppppimmFaFHpEeEEEExEamp')
```

If `provide()` is applied multiple times, any call to the function
repeats successively to match that number, and teardowns are performed
at the end of each invocation (see
[Ensuring Teardown](#ensuring-teardown)). The execution of the
decorators occurs in the usual Pythonic order, i.e. nearest first. The
function returns the result of the last call.

```python
@provide(
    password=password,
    username=choices(ascii_lowercase, k=between(4, 12))
)
@provide(
    password=None,
    username=None
)
def credentials(username, password):
    global times
    times += 1
    return username, password
```
```pycon
>>> times = 0
>>> credentials()
('sbtft', 'Ax4LzILzILZIZLpIpzIzLpzILLZIpLL')
>>> times
2
```

##

$\large \color{gray}protestr.\color{black}\textbf{resolve(spec)}$

Resolve a spec.

The spec can be `int`, `float`, `complex`, `float`, `str`, a tuple, a
list, a set, a dictionary, or anything callable without args.

```pycon
>>> resolve(str)
'jKKbbyNgzj'
```
```pycon
>>> resolve({"number": int})
{'number': 925}
```
```pycon
>>> resolve({str: str})
{'RRAIvpJLKAqpLQNNVNXmExe': 'raaqSzSdfCIYxbIhuTGdxi'}
```
```pycon
>>> from random import random
>>> resolve(random)
0.8177445321472337
```
```pycon
>>> class Foo:
...     def __init__(self):
...         self.message = "Foo instantiated"
...
>>> resolve(Foo).message
'Foo instantiated'
```

##

$\large \color{gray}protestr.specs.\color{black}\textbf{between(x, y)}$

Return a spec to choose a number between `x` and `y`.

`x` and `y` must be specs that evaluate to numbers. If both `x` and `y`
evaluate to integers, the resulting number is also an integer.

```pycon
>>> between(10, -10)()
>>> int_spec()
3
```
```pycon
>>> between(-10, 10.0)()
-4.475185425413375
```
```pycon
>>> between(int, int)()
452
```

##

$\large \color{gray}protestr.specs.\color{black}\textbf{choice(*elems)}$

Return a spec to choose a member from `elems`.

```pycon
>>> colors = ["red", "green", "blue"]
>>> choice(colors)()
'green'
```
```pycon
>>> choice(str)() # a char from a generated str
'T'
```
```pycon
>>> choice(str, str, str)() # an str from three generated str objects
'NOBuybxrf'
```

##

$\large \color{gray}protestr.specs.\color{black}\textbf{choices(*elems, k)}$

Returns a spec to choose `k` members from `elems` with replacement.

`k` must be a spec that evaluates to some natural number.

```pycon
>>> choices(["red", "green", "blue"], k=5)()
['blue', 'red', 'green', 'blue', 'green']
```
```pycon
>>> choices("red", "green", "blue", k=5)()
('red', 'blue', 'red', 'blue', 'green')
```
```pycon
>>> choices(ascii_letters, k=10)()
'OLDpaXOGGj'
```

##

$\large \color{gray}protestr.specs.\color{black}\textbf{sample(*elems, k)}$

Return a spec to choose `k` members from `elems` without replacement.

`k` must be a spec that evaluates to some natural number.

```pycon
>>> colors = ["red", "green", "blue"]
>>> sample(colors, k=2)()
['blue', 'green']
```
```pycon
>>> sample("red", "green", "blue", k=3)()
('red', 'blue', 'green')
```
```pycon
>>> sample(ascii_letters, k=10)()
'tkExshCbTi'
```
```pycon
>>> sample([int] * 3, k=between(2, 3))() # 2–3 out of 3 integers
[497, 246]
```

##

$\large \color{gray}protestr.specs.\color{black}\textbf{recipe(*specs, then)}$

Return a spec to get the result of calling a given function with some
given specs resolved.

`then` must be callable with a collection of the resolved specs.

```pycon
>>> recipe(
...     sample(ascii_letters, k=5),
...     sample(digits, k=5),
...     then="".join
... )()
'yDnjU16430'
```

## Working Example

The complete working example available in
[tests/examples/](https://github.com/Grimmscorpp/protestr/tree/main/tests/examples)
should be self-explanatory. If not, please refer to
[Getting Started](#getting-started) and [Documentation](#documentation)
to become familiar with a few concepts. Here's an excerpt:

```python
# tests/examples/test_examples.py

import tests.examples.specs as specs
...
...

class TestExamples(unittest.TestCase):
    ...
    ...

    @provide(
        password=recipe(
            choices(digits, k=5),
            choices(ascii_uppercase, k=5),
            then="".join
        ),
        expected="Password must contain a lowercase letter",
        db=specs.testdb,
        user=specs.user
    )
    @provide(
        password=recipe(
            choices(digits, k=5),
            choices(ascii_lowercase, k=5),
            then="".join
        ),
        expected="Password must contain an uppercase letter",
        db=specs.testdb,
        user=specs.user
    )
    @provide(
        password=choices(ascii_letters, k=8),
        expected="Password must contain a number",
        db=specs.testdb,
        user=specs.user
    )
    @provide(
        password=choices(str, k=7),
        expected="Password must be at least 8 chars",
        db=specs.testdb,
        user=specs.user
    )
    @patch("tests.examples.fakes.os.getenv")
    def test_insert_user_with_invalid_password(
        self, getenv, db, user, password, expected
    ):
        getenv.side_effect = [8]

        user.password = password

        try:
            db.insert(user)
        except Exception as e:
            message, = e.args

        self.assertEqual(message, expected)

        getenv.assert_called_once_with("MIN_PASSWORD_LEN")

    ...
    ...

if __name__ == "__main__":
    unittest.main()
```

If you're curious, here are the specs we defined for the example:

```python
# tests/examples/specs.py

from tests.examples.fakes import User, UsersDB
...
...

@provide(
    digit=choice(digits),                 # password to contain a
    uppercase=choice(ascii_uppercase),    # number, an uppercase and a
    lowercase=choice(ascii_lowercase),    # lowercase letter, and be
    chars=choices(str, k=between(5, 100)) # 8–15 characters long
)
def password(uppercase, lowercase, digit, chars):
    return "".join((uppercase, lowercase, digit, chars))


@provide(
    id=str,
    firstname=choice("John", "Jane", "Orange"),
    lastname=choice("Smith", "Doe", "Carrot"),
    username=choices(ascii_lowercase, k=between(5, 10)),
    password=password
)
def user(id, firstname, lastname, username, password):
    return User(id, firstname, lastname, username, password)


@provide(users=3*[user])
def testdb(users):
    return UsersDB(users)
```

## License

`protestr` is distributed under the terms of the
[MIT](https://spdx.org/licenses/MIT.html) license.
