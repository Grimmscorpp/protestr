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
   1. [Tearing Down](#tearing-down)
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
   ...     lat=single("equator", "north pole", "south pole"),
   ...     alt=int
   ... )
   ('north pole', -107.37336459941672, 581)
   ```

   Here, `lat` and `alt` have been overridden with `single` (a built-in
   spec) and `int`. Generally, specs created with `provide()` can be
   passed any spec to override defaults as long as they are passed
   intact. Consider the following incorrect approach:

   ```pycon
   >>> geo_coord(
   ...     lat=str(single("equator", "north pole", "south pole")) # ❌
   ... )
   ('<function[TRIMMED]98AF80>', -126.77844430204937, 678.4366330272486)
   ```

   It didn't work as expected because `single` was consumed by `str`, so
   it wasn't intact when passed to `geo_coord`. Consider another
   example:

   ```pycon
   >>> geo_coord(
   ...     lat=merged(
   ...         single("equator", "arctic circle", "antarctic circle"),
   ...         between(5, 10),
   ...         func=lambda them: " ± ".join(str(x) for x in them)
   ...     )
   ... )
   ('antarctic circle ± 7', 93.7335784938644, 388.76826219877256)
   ```

   Passing specs intact to one another is perfectly okay.

1. Resolve with `resolve`:

   ```
   >>> from protestr import resolve
   >>> resolve(geo_coord)
   (-68.79360870922969, 8.200171266070214, 691.5305890425291)
   ```

   `resolve` also works with other types, as mentioned in
   [Documentation](#documentation).

1. Provide with `provide()`:

   ```python
   @provide(geo_coords=2*[geo_coord])
   def line(geo_coords):
       start, end = geo_coords
       return start, end
   ```

   `provide()` is the decorator version of `resolve` that accepts
   multiple specs as keyword args.

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

### Tearing Down

Good fixture design demands remembering to dispose of resources at the
end of tests. Protestr takes care of it out of the box with the
`__teardown__` function. Whenever a `provide()`-applied function returns
or terminates abnormally, it looks for `__teardown__` on each (resolved)
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

$\huge \color{gray}protestr.\color{black}\textbf{provide(**kwdspecs)}$

Provides specs to a function as keyword args. The names in the keywords
may be in any order in the parameters. The function is thus modified to
be callable with the provided args omitted or specified to override.

```pycon
>>> @provide(
...     password=merged(
...         single(ascii_uppercase),
...         single(ascii_lowercase),
...         single(digits),
...         permutation(str, k=between(5, 100)),
...         func="".join
...     ),
...     username=permutation(ascii_lowercase, k=between(4, 12))
... )
... def credentials(username, password):
...     return username, password
...
>>> credentials()
('cgbqkmsehf', 'Pr8LOipCBKCBkAxbbKykppKkALxykKLOiKpiy')
>>> credentials(username="johndoe")
('johndoe', 'En2HivppppimmFaFHpEeEEEExEamp')
```

##

$\huge \color{gray}protestr.\color{black}\textbf{resolve(spec)}$

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

$\huge \color{gray}protestr.specs.\color{black}\textbf{between(x, y)}$

Returns a spec that resolves to a number between `x` and `y`, where `x`
and `y` are specs that resolve to numbers. If both `x` and `y` resolve
to integers, the resulting number is also an integer.

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

$\huge \color{gray}protestr.specs.\color{black}\textbf{single(*elems)}$

Returns a spec that resolves to some member in `elems`, where `elems` is
a spec that resolves to some iterable.

```pycon
>>> colors = ["red", "green", "blue"]
>>> single(colors)()
'green'

>>> single(str)() # single char from a generated str
'T'

>>> single(str, str, str)() # single str from three str objects
'NOBuybxrf'
```

##

$\huge \color{gray}protestr.specs.\color{black}\textbf{combination(*elems, k)}$

Returns a spec that resolves to a combination of `k` members from
`elems` without repetition, where `k` and `elems` are specs that resolve
to some natural number and collection, respectively.

```pycon
>>> colors = ["red", "green", "blue"]
>>> combination(colors, k=2)()
['blue', 'green']

>>> combination("red", "green", "blue", k=3)()
('red', 'blue', 'green')

>>> combination(ascii_letters, k=10)()
'tkExshCbTi'

>>> combination([int] * 3, k=between(2, 3))() # 2–3 out of 3 integers
[497, 246]
```

##

$\huge \color{gray}protestr.specs.\color{black}\textbf{permutation(*elems, k)}$

Returns a spec that resolves to a permutation of `k` members from
`elems` with repetition, where `k` and `elems` are specs that resolve to
some natural number and collection, respectively. It's usage is similar
to `combination`.

```pycon
>>> permutation("abc", k=5)()
'baaca'
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
        shortpass=permutation(str, k=7),
        longpass=permutation(str, k=16)
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
    id=str,
    firstname=single("John", "Jane", "Orange"),
    lastname=single("Smith", "Doe", "Carrot"),
    username=permutation(ascii_letters, k=between(5, 10)),
    password=merged(
        single(digits),                     # password to contain a
        single(ascii_uppercase),            # number, an uppercase and
        single(ascii_lowercase),            # a lowercase letter and be
        permutation(str, k=between(5, 12)), # 8–15 characters long
        func="".join
    )
)
def user(id, firstname, lastname, username, password):
    return User(id, firstname, lastname, username, password)


@provide(users=3*[user])
def testdb(users):
    return UsersDB(users)
```

## License

`protestr` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
