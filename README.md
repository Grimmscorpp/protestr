# Protestr: Pro Test Fixture Provider

[![PyPI - Version](https://img.shields.io/pypi/v/protestr.svg)](https://pypi.org/project/protestr)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/protestr.svg)](https://pypi.org/project/protestr)

-----

Protestr is a simple, powerful Python library that generates versatile
[fixtures](#specs-and-fixtures) based on **your rules.** It's designed to
maximize focus on acts and assertions by handling the complexities of fixture
management. Its intuitive [API](#documentation) lets you:

- **Re-run tests**  
  Provide dynamic fixtures using dependency injection, repeating a test for different
  scenarios instead of duplicating it with hardly any change.

- **Ensure teardown**  
  Have your defined cleanup logic run consistently after every test run.

- **Use anywhere**  
  Integrate seamlessly with all popular Python testing frameworks, such as `unittest`,
  `pytest`, and `nose2`, facing zero disruption to your existing testing practices.

The examples in this doc have been carefully crafted to help you master its concepts and
get the best out of it.

> [!NOTE]
> Protestr was tested with Protestr.

## Next Up

- [Quick Demo](#quick-demo)
- [Getting Started](#getting-started)
  - [Installation](#installation)
  - [Specs and Fixtures](#specs-and-fixtures)
  - [Creating Specs](#creating-specs)
  - [Ensuring Teardown](#ensuring-teardown)
- [Documentation](#documentation)
  - [`protestr`](#protestr)
  - [`protestr.specs`](#protestrspecs)
- [License](#license)

## Quick Demo

The test below **won't run** because the test runner can't provide `users` and `mongo`.

```python
import unittest
from unittest.mock import patch as mock


class TestWithMongo(unittest.TestCase):
    @mock("examples.lib.os")
    def test_add_to_users_db(
        self,   #  ✅  Provided by `unittest`
        os,     #  ✅  Provided by `mock()`
        users,  #  ❌  Unexpected param `users`
        mongo,  #  ❌  Unexpected param `mongo`
    ):
        os.environ.__getitem__.return_value = "localhost"

        add_to_users_db(users)

        added = mongo.client.users_db.users.count_documents({})
        self.assertEqual(added, len(users) if users else 0)
```

Protestr allows you to **provide fixtures** to generate these parameters elegantly. You
can also chain multiple fixtures to **repeat the test** for different test cases.

```python
...
from protestr import provide
from examples.specs import User, MongoDB


class TestWithMongo(unittest.TestCase):
    @provide(              #  ▶️  Fixture Ⅰ
        users=[User] * 3,  #  ✨  Generate 3 test users. Spin up a MongoDB container.
        mongo=MongoDB,     #  🔌  After each test, disconnect and remove the container.
    )
    @provide(users=[])     #  ▶️  Fixture Ⅱ: Patch the above fixture to generate 0 users
    @provide(users=None)   #  ▶️  Fixture Ⅲ
    @mock("examples.lib.os")
    def test_add_to_users_db(self, os, users, mongo):
        os.environ.__getitem__.return_value = "localhost"

        add_to_users_db(users)

        added = mongo.client.users_db.users.count_documents({})
        self.assertEqual(added, len(users) if users else 0)
```

> [!TIP]
> The top-most `provide()` call must declare all specs. Subsequent ones should specify
> patches (what changed) from the previous test case.

In the example above, `User` and `MongoDB` are user-defined **specs**—the blueprints for
generating test data.

Protestr offers some great specs in [`protestr.specs`](#protestrspecs) and makes it
*incredibly* easy to define new ones (explained in "[Creating Specs](#creating-specs)").

```python
from protestr.specs import between


@provide(id=between(1, 99), name=str, password=str)
class User:
    def __init__(self, id, name, password):
        self.id = id
        self.name = name
        self.password = password


class MongoDB:
    def __init__(self):
        self.container = docker.from_env().containers.run(
            "mongo", detach=True, ports={27017: 27017}
        )
        self.client = pymongo.MongoClient("localhost", 27017)

    def __teardown__(self):      #  ♻️  After each test:
        self.client.close()      #  🔌  Disconnect the container
        self.container.stop()    #  🛑  Stop the container
        self.container.remove()  #  🧹  Remove the container
```

Find the complete example in [examples/](examples/).

## Getting Started

### Installation

Install [`protestr`](https://pypi.org/project/protestr/) from PyPI:

```shell
pip install protestr
```

### Specs and Fixtures

Specs are blueprints for generating test data. A fixture is a combination of specs
provided to a class/function—usually a test method—using `provide()`.

Specs are **resolved** by Protestr to generate usable data. There are three types of
specs:

1. **Python primitives:** `int`, `float`, `complex`, `bool`, or `str`.

1. **Classes and functions that are callable without args.**  
   If a constructor or a function contains required parameters, it can be transformed
   into a spec by auto-providing those parameters using `provide()` (explained in
   "[Creating Specs](#creating-specs)").

1. **Tuples, lists, sets, or dictionaries of specs** in any configuration, such as a
   list of lists of specs.

Specs are resolved in two ways:

1. **By resolving**

   ```pycon
   >>> from protestr import resolve
   >>> from protestr.specs import choice
   >>> bits = [choice(0, 1)] * 8
   >>> resolve(bits)
   [1, 0, 0, 1, 1, 0, 1, 0]
   ```

1. **By calling/resolving a *spec-provided* class/function**
   ```pycon
   >>> from protestr import provide
   >>> @provide(where=choice("home", "work", "vacation"))
   ... def test(where):
   ...     return where
   ...
   >>> test()
   'vacation'
   >>> resolve(test)
   'home'
   ```

The resolution of specs is **recursive**. If a spec produces another spec, Protestr will
resolve that spec, and so on.

```python
from protestr import provide


@provide(x=int, y=int)
def point(x, y):
    return x, y


def triangle():
    return [point] * 3


print(resolve(triangle))
# [(971, 704), (268, 581), (484, 548)]
```

> [!TIP]
> A spec-provided class/function itself becomes a spec and can be resolved recursively.
>
> ```python
> >>> @provide(n=int)
> ... def f(n):
> ...     def g():
> ...         return n
> ...     return g
> ...
> >>> resolve(f)
> 784
> ``````

Protestr simplifies spec creation so that you can create custom specs effortlessly for
*your* testing requirements.

### Creating Specs

Creating a spec usually takes two steps:

1. **Write a class/function**

   ```python
   class GeoCoordinate:
       def __init__(self, latitude, longitude, altitude):
           self.latitude = latitude
           self.longitude = longitude
           self.altitude = altitude


   # def geo_coordinate(latitude, longitude, altitude):
   #     return latitude, longitude, altitude
   ```
 
1. **Provide specs for required parameters** *if any*

   ```python
   @provide(
       latitude=between(-90.0, 90.0),
       longitude=between(-180.0, 180.0),
       altitude=float,
   )
   class GeoCoordinate:
       def __init__(self, latitude, longitude, altitude):
           self.latitude = latitude
           self.longitude = longitude
           self.altitude = altitude


   # @provide(
   #     latitude=between(-90.0, 90.0),
   #     longitude=between(-180.0, 180.0),
   #     altitude=float,
   # )
   # def geo_coordinate(latitude, longitude, altitude):
   #     return latitude, longitude, altitude
   ```

Thus, our new spec is prime and ready!

```pycon
>>> resolve(GeoCoordinate).altitude
247.70713408051304
>>> GeoCoordinate().altitude
826.6117116092906
>>> GeoCoordinate(altitude=int).altitude
299
```

```python
import unittest
from protestr import provide


class TestLocations(unittest.TestCase):

    @provide(locs=[GeoCoordinate] * 100)

    def test_locations(self, locs):

        self.assertEqual(100, len(locs))

        for loc in locs:
            self.assertTrue(hasattr(loc, "latitude"))
            self.assertTrue(hasattr(loc, "longitude"))
            self.assertTrue(hasattr(loc, "altitude"))


if __name__ == "__main__":
    unittest.main()
```

Find more sophisticated usages in the [Documentation](#documentation).

### Ensuring Teardown

Good fixture design demands remembering to dispose of resources at the end of tests.
Protestr takes care of it out of the box with the `__teardown__` function. Whenever a
`provide()`-applied function returns or terminates abnormally, it looks for
`__teardown__` in each (resolved) object it provided and invokes it on the object if
found. So, all you need to do is define `__teardown__` once in a class, and it will be
called every time you provide one.

```python
class MongoDB:
    def __init__(self):
        self.container = docker.from_env().containers.run(
            "mongo", detach=True, ports={27017: 27017}
        )
        self.client = pymongo.MongoClient("localhost", 27017)

    def __teardown__(self):
        self.client.close()
        self.container.stop()
        self.container.remove()
```

## Documentation

### `protestr`

$\large\textcolor{gray}{@protestr.}\textbf{provide(**specs)}$

Transform a class/function to auto-supply args when invoked.

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

The specs are provided implicitly from keyword args in `provide()` to the matching
parameters of the function when called with those args omitted.

```pycon
>>> credentials()
('cgbqkmsehf', 'Pr8LOipCBKCBkAxbbKykppKkALxykKLOiKpiy')
```

When specified as keyword args, they override the original specs.

```pycon
>>> credentials(username="johndoe")
('johndoe', 'En2HivppppimmFaFHpEeEEEExEamp')
```

If `provide()` is applied multiple times, the function runs as many times (when
invoked), and teardowns are performed at the end of each invocation (see
[Ensuring Teardown](#ensuring-teardown)). This trait can be leveraged to re-run tests
for different test cases.

```python
class TestFactorial(unittest.TestCase):
    @provide(n=0, expected=1)
    @provide(n=1)
    @provide(n=5, expected=120)
    def test_factorial_valid_number(self, n, expected):
        self.assertEqual(expected, factorial(n))

    @provide(n=float, expected="n must be a whole number")
    @provide(n=between(-1000, -1), expected="n must be >= 0")
    def test_factorial_invalid_number(self, n, expected):
        try:
            factorial(n)
        except Exception as e:
            (message,) = e.args

        self.assertEqual(expected, message)
```

##

$\large\textcolor{gray}{protestr.}\textbf{resolve(spec)}$

Resolve a spec.

Specs can be any of the following types:

1. **Python primitives:** `int`, `float`, `complex`, `bool`, or `str`.

1. **Classes and functions that are callable without args.**  
   If a constructor or a function contains required parameters, it can be transformed
   into a spec by auto-providing those parameters using `provide()`.

1. **Tuples, lists, sets, or dictionaries of specs** in any configuration, such as a
   list of lists of specs.

```pycon
>>> resolve(str)
'jKKbbyNgzj'
```
```pycon
>>> resolve([bool] * 3)
[False, False, True]
```
```pycon
>>> resolve({"name": str})
{'name': 'raaqSzSdfCIYxbIhuTGdxi'}
```
```pycon
>>> class Foo:
...     def __init__(self):
...         self.who = "I'm Foo"
...
>>> resolve(Foo).who
"I'm Foo"
```

##

### `protestr.specs`

$\large\textcolor{gray}{protestr.specs.}\textbf{between(x, y)}$

Return a spec representing a number between `x` and `y`.

`x` and `y` must be specs that evaluate to numbers. If both `x` and `y` evaluate to
integers, the resulting number is also an integer.

```pycon
>>> resolve(between(10, -10))
3
```
```pycon
>>> resolve(between(-10, 10.0))
-4.475185425413375
```
```pycon
>>> resolve(between(int, int))
452
```

##

$\large\textcolor{gray}{protestr.specs.}\textbf{choice(*elems)}$

Return a spec representing a member of `elems`.

```pycon
>>> colors = ["red", "green", "blue"]
>>> resolve(choice(colors))
'green'
```
```pycon
>>> resolve(choice(str)) # a char from a generated str
'T'
```
```pycon
>>> resolve(choice(str, str, str)) # an str from three generated str objects
'NOBuybxrf'
```

##

$\large\textcolor{gray}{protestr.specs.}\textbf{choices(*elems, k)}$

Return a spec representing `k` members chosen from `elems` with replacement.

`k` must be a spec that evaluates to some natural number.

```pycon
>>> resolve(choices(["red", "green", "blue"], k=5))
['blue', 'red', 'green', 'blue', 'green']
```
```pycon
>>> resolve(choices("red", "green", "blue", k=5))
('red', 'blue', 'red', 'blue', 'green')
```
```pycon
>>> resolve(choices(ascii_letters, k=10))
'OLDpaXOGGj'
```

##

$\large\textcolor{gray}{protestr.specs.}\textbf{sample(*elems, k)}$

Return a spec representing `k` members chosen from `elems` without replacement.

`k` must be a spec that evaluates to some natural number.

```pycon
>>> colors = ["red", "green", "blue"]
>>> resolve(sample(colors, k=2))
['blue', 'green']
```
```pycon
>>> resolve(sample("red", "green", "blue", k=3))
('red', 'blue', 'green')
```
```pycon
>>> resolve(sample(ascii_letters, k=10))
'tkExshCbTi'
```
```pycon
>>> resolve(sample([int] * 3, k=between(2, 3))) # generate 3, pick 2, for demo only
[497, 246]
```

##

$\large\textcolor{gray}{protestr.specs.}\textbf{recipe(*specs, then)}$

Return a spec representing the result of calling a given function with some given specs
resolved.

`then` must be callable with a collection containing the resolved specs.

```pycon
>>> from string import ascii_letters, digits
>>> resolve(
...     recipe(
...         sample(ascii_letters, k=5),
...         sample(digits, k=5),
...         then="-".join,
...     )
... )
'JzRYQ-51428'
```

## License

`protestr` is distributed under the terms of the
[MIT](https://spdx.org/licenses/MIT.html) license.
