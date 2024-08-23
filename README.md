# protestr

[![PyPI - Version](https://img.shields.io/pypi/v/protestr.svg)](https://pypi.org/project/protestr)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/protestr.svg)](https://pypi.org/project/protestr)

-----

Pro test fixture configurator in Python, for Python, tested with
Protester itself.

## Table of Contents

1. [Rationale](#rationale)
1. [Getting Started](#getting-started)
   1. [Installation](#installation)
   1. [Creating Specs](#creating-specs)
   1. [Ensuring Teardown](#ensuring-teardown)
1. [Documentation](#documentation)
1. [Working Example](#working-example)
1. [License](#license)

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

### Creating Specs

A fixture is technically a set of specifications (specs) "provided" to a
function to resolve into actual data. The specs — usually functions —
describe how different parts of the fixture form. Protestr offers a few
built-in specs in `protestr.specs`, but you may need more. So, let's
create an example geo-coordinate spec to start with. A valid
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

   Here, `lat` and `alt` have been overridden with `choice()` (a
   built-in spec) and `int`. Remember, **specs created with `provide()`
   can be passed any spec to override defaults as long as they are
   passed intact.** Consider the following incorrect approach:

   ```pycon
   >>> geo_coord(
   ...     lat=str(choice(23.4394, -23.4394)) # ❌
   ... )
   ('<function[TRIMMED]98AF80>', -126.77844430204937, 678.4366330272486)
   ```

   What went wrong in the example above? The output of `choice()` (a
   spec) got consumed by `str`, so it wasn't intact when assigned to
   `lat`. Consider another example:

   ```pycon
   >>> geo_coord(
   ...     lat=choice(
   ...         sample("equator", "north pole", "south pole", k=2)
   ...     )
   ... )
   ('north pole', -140.1178603399875, 431.79874634752593)
   ```

   Although it's unnecessary to pass `sample()` to `choice()`, the
   example above is to demonstrate that passing intact specs to one
   another is perfectly okay.

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
object it provided and invokes it on the object if found. Any exceptions
raised during the process are accumulated and reraised together as
`Exception(ex1, ex2, ..., exn)`. So, all you need to do is define
`__teardown__` once in a class, and it will be called every time you
provide one.

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

$\large \color{gray}protestr.\color{black}\textbf{provide(**kwdspecs)}$

Provides specs to a function as keyword args. The names in the keywords
may be in any order in the parameters. The function is thus modified to
be callable with the provided args omitted or specified to override.

```pycon
>>> @provide(
...     uppercase=choice(ascii_uppercase),
...     lowercase=choice(ascii_lowercase),
...     digit=choice(digits),
...     chars=choices(str, k=between(5, 100))
... )
... def password(uppercase, lowercase, digit, chars):
...     return "".join((uppercase, lowercase, digit, chars))

>>> @provide(
...     password=password,
...     username=choices(ascii_lowercase, k=between(4, 12))
... )
... def credentials(username, password):
...     return username, password

>>> credentials()
('cgbqkmsehf', 'Pr8LOipCBKCBkAxbbKykppKkALxykKLOiKpiy')

>>> credentials(username="johndoe")
('johndoe', 'En2HivppppimmFaFHpEeEEEExEamp')
```

##

$\large \color{gray}protestr.\color{black}\textbf{resolve(spec)}$

Resolves a spec, which can be an `int`, `float`, `complex`, `float`,
`str`, tuple, list, set, dictionary, or anything callable without args.

```pycon
>>> resolve(str)
'jKKbbyNgzj'

>>> resolve({"number": int})
{'number': 925}

>>> resolve({str: str})
{'RRAIvpJLKAqpLQNNVNXmExe': 'raaqSzSdfCIYxbIhuTGdxi'}

>>> from random import random
>>> resolve(random)
0.8177445321472337

>>> class Foo:
...     def __init__(self):
...         self.message = "Foo instantiated"
...
>>> resolve(Foo).message
'Foo instantiated'
```

##

$\large \color{gray}protestr.specs.\color{black}\textbf{between(x, y)}$

Returns a spec to resolve a number between `x` and `y`, where `x` and
`y` are specs that evaluate to numbers. If both `x` and `y` evaluate to
integers, the resulting number is also an integer.

```pycon
>>> between(10, -10)()
>>> int_spec()
3

>>> between(-10, 10.0)()
-4.475185425413375

>>> between(int, int)()
452
```

##

$\large \color{gray}protestr.specs.\color{black}\textbf{choice(*elems)}$

Returns a spec to choose a member from `elems`, where `elems` is a spec
that evaluates to some iterable.

```pycon
>>> colors = ["red", "green", "blue"]
>>> choice(colors)()
'green'

>>> choice(str)() # chosen char from a generated str
'T'

>>> choice(str, str, str)() # chosen str from three str objects
'NOBuybxrf'
```

##

$\large \color{gray}protestr.specs.\color{black}\textbf{choices(*elems, k)}$

Returns a spec to choose `k` members from `elems` with replacement,
where `k` and `elems` are specs that evaluate to some natural number
and collection, respectively. It's usage is similar to `sample()`.

```pycon
>>> choices("abc", k=5)()
'baaca'
```

##

$\large \color{gray}protestr.specs.\color{black}\textbf{sample(*elems, k)}$

Returns a spec to choose `k` members from `elems` without replacement,
where `k` and `elems` are specs that evaluate to some natural number
and collection, respectively.

```pycon
>>> colors = ["red", "green", "blue"]
>>> sample(colors, k=2)()
['blue', 'green']

>>> sample("red", "green", "blue", k=3)()
('red', 'blue', 'green')

>>> sample(ascii_letters, k=10)()
'tkExshCbTi'

>>> sample([int] * 3, k=between(2, 3))() # 2–3 out of 3 integers
[497, 246]
```

## Working Example

The complete working example available in
[tests/example/](https://github.com/Grimmscorpp/protestr/tree/main/tests/example)
should be self-explanatory. If not, please refer to
[Getting Started](#getting-started) and [Documentation](#documentation)
to become familiar with a few concepts. Here's an excerpt:

```python
# tests/examples/test_example.py

import tests.example.specs as specs
...
...

class TestExample(unittest.TestCase):
    ...
    ...

    @provide(
        db=specs.testdb,
        user=specs.user,
        shortpass=choices(str, k=7),
        longpass=choices(str, k=16)
    )
    @patch("tests.example.fakes.getenv")
    def test_insert_user_with_invalid_password_lengths_fails(
        self, getenv, db, user, shortpass, longpass
    ):
        getenv.side_effect = lambda env: \
            8 if env == "MIN_PASSWORD_LEN" else 15

        for pw in (shortpass, longpass):
            user.password = pw

            try:
                db.insert(user)
            except Exception as e:
                message, = e.args

            self.assertEqual(
                message, "Password size must be between 8 and 15"
            )

        self.assertEqual(getenv.mock_calls, [
            call("MIN_PASSWORD_LEN"),
            call("MAX_PASSWORD_LEN"),
            call("MIN_PASSWORD_LEN"),
            call("MAX_PASSWORD_LEN")
        ])

    ...
    ...

if __name__ == "__main__":
    unittest.main()
```

If you're curious, here are the specs we created for the example:

```python
# tests/examples/specs.py

from tests.example.fakes import User, UsersDB
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
