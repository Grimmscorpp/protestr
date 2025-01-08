# Protestr: Pro Test Fixture Provider

[![PyPI - Version](https://img.shields.io/pypi/v/protestr.svg)](https://pypi.org/project/protestr)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/protestr.svg)](https://pypi.org/project/protestr)
![test](https://github.com/Grimmscorpp/protestr/actions/workflows/lint-and-test.yml/badge.svg)
[![PyPI Downloads](https://static.pepy.tech/badge/protestr)](https://pepy.tech/projects/protestr)

Protestr is a simple, powerful [fixture](#specs-and-fixtures) provider for Python tests.
Whether writing unit tests, integration tests, or anything in between, Protestr's
intuitive [API](#documentation) lets you generate versatile fixtures for your test cases
and inject them as dependencies on demand. It's designed to maximize focus on acts and
assertions by simplifying the complexities of fixture management. Its declarative syntax
allows you to:

- **Re-run tests**  
  Provide dynamic test dependencies, inject on demand, and re-run a test for different
  scenarios instead of duplicating it with little change.

- **Ensure teardown**  
  Have your defined cleanup logic run consistently after every test run.

- **Use anywhere**  
  Integrate seamlessly with all popular Python testing frameworks, such as `unittest`,
  `pytest`, and `nose2`, facing zero disruption to your existing testing practices.

The examples in this doc have been carefully crafted to help you master its concepts and
get the most out of it.

> [!NOTE]
> Protestr was tested with Protestr.

## Next Up

- [Quick Examples](#quick-examples)
- [Getting Started](#getting-started)
  - [Installation](#installation)
  - [Specs and Fixtures](#specs-and-fixtures)
  - [Creating Specs](#creating-specs)
  - [Using Specs](#using-specs)
  - [Ensuring Teardown](#ensuring-teardown)
- [Documentation](#documentation)
  - [`protestr`](#protestr)
  - [`protestr.specs`](#protestrspecs)
- [License](#license)

## Quick Examples

This test expects a MongoDB container and some test users, which the test framework
can't provide out of the box.

```python
import unittest
from unittest.mock import patch as mock


class TestWithMongo(unittest.TestCase):
    @mock("examples.lib.os")
    def test_add_to_users_db_should_add_all_users(
        self,   #  ✅  Provided by `unittest`
        os,     #  ✅  Provided by `mock()`
        users,  #  ❌  Unexpected param `users`
        mongo,  #  ❌  Unexpected param `mongo`
    ):
        os.environ.__getitem__.return_value = "localhost"

        add_to_users_db(users)

        added = mongo.client.users_db.users.count_documents({})
        self.assertEqual(added, len(users))
```

With Protestr, you can define a *fixture* to generate and inject these dependencies
elegantly. You can also provide multiple fixtures to *repeat* the test for different
scenarios.

```python
...
from protestr import provide
from examples.specs import User, MongoDB


class TestWithMongo(unittest.TestCase):
    @provide(              #  ▶️  Fixture Ⅰ
        users=[User] * 3,  #  ✨  Generate 3 test users. Spin up a MongoDB container.
        mongo=MongoDB,     #  🔌  After each test, disconnect and remove the container.
    )
    @provide(users=[])     #  ▶️  Fixture Ⅱ: Patch the first fixture.
    @mock("examples.lib.os")
    def test_add_to_users_db_should_add_all_users(self, os, users, mongo):
        os.environ.__getitem__.return_value = "localhost"

        add_to_users_db(users)

        added = mongo.client.users_db.users.count_documents({})
        self.assertEqual(added, len(users))
```

Here, `User` and `MongoDB` are *specs* for generating test data/infrastructure.

> [!NOTE]
> When multiple `provide()` decorators are chained, their order of execution is **top to
> bottom.** The first one must specify all specs in the fixture, whereas others only
> need to provide patches of the *first* fixture.

Protestr uses specs supplied in `provide()` to generate test data/infrastructure. When
specs are specified as *keyword* args in `provide()`, they are also injected into the
target (method/class/spec) through matching parameters, if any.

Keyword specs can also be patched in chained `provide()` calls (as shown above) or
overridden altogether (explained in "[Using Specs](#using-specs)"). On the other hand,
non-keyword specs are useful for generating indirect test dependencies, such as
containers running in the *background.*

```python
class TestWithRedis(unittest.TestCase):
    @provide(
        Redis,                #  🥷  Spin up a Redis container in the background.
        response={str: str},
    )
    @provide(response=None)   #  🥷  Recreate the container in another scenario.
    def test_cached_should_cache_fn(self, response):
        costly_computation = MagicMock()

        @cached
        def fn():
            costly_computation()
            return response

        self.assertEqual(response, fn())
        self.assertEqual(response, fn())

        costly_computation.assert_called_once()
```

Protestr offers some great specs in [`protestr.specs`](#protestrspecs) and makes it
*incredibly easy* to define new ones (detailed in "[Creating Specs](#creating-specs)").
Following are the definitions of the specs used above.

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

    def __teardown__(self):      #  ♻️  Ensure teardown after each test.
        self.client.close()
        self.container.stop()
        self.container.remove()


class Redis:
    def __init__(self):
        self.container = docker.from_env().containers.run(
            "redis:8.0-M02", detach=True, ports={6379: 6379}
        )

        # wait for the port
        time.sleep(0.1)

    def __teardown__(self):      #  ♻️  Ensure teardown after each test.
        self.container.stop()
        self.container.remove()
```

See also: [examples/](examples/).

## Getting Started

### Installation

Install [`protestr`](https://pypi.org/project/protestr/) from PyPI:

```shell
pip install protestr
```

### Specs and Fixtures

Specs are blueprints for generating test data/infrastructure. A fixture is a combination
of specs provided to a class/function—usually a test method—using `provide()`.

Specs are *resolved* by Protestr to generate usable values and entities. There are three
types of specs:

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
   >>> @provide(where=choice("home", "work", "vacation"))
   ... def test(where):
   ...     return where
   ...
   >>> test()
   'vacation'
   >>> resolve(test)
   'home'
   ```

The resolution of specs is *recursive*. If a spec produces another spec, Protestr will
resolve that spec, and so on.

```python
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
 
1. **Provide specs for required parameters,** *if any*

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

Thus, our new spec is ready for use like any other spec.

### Using Specs

Specs can be used in the following ways.

- **Resolve**

  ```pycon
  >>> resolve(GeoCoordinate).altitude
  247.70713408051304
  >>> GeoCoordinate().altitude
  826.6117116092906
  ```

- **Override**

  ```pycon
  >>> coord = GeoCoordinate(altitude=int)  #  Override the `altitude` spec.
  >>> coord.altitude
  299
  ```

- **Provide**

  ```python
  import unittest
  from protestr import provide
  
  
  class TestLocations(unittest.TestCase):
  
      @provide(locs=[GeoCoordinate] * 100)  #  Provide 💯 of them.
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

Protestr ensures teardown of resources out of the box, so you don't need to remember to
do it. Every time a `provide()`-applied function terminates—naturally or
abnormally—Protestr checks each spec in the fixture to see if it contains a
`__teardown__` function. If found, the function is called, thus tearing down the
generated object based on *your* cleanup rules without fail.

```python
class MongoDB:
    def __init__(self):
        ...

    def __teardown__(self):
        self.client.close()
        self.container.stop()
        self.container.remove()
```

## Documentation

### `protestr`

$\large\textcolor{gray}{@protestr.}\textbf{provide(\*specs, \*\*kwspecs)}$

Transform a class/function to automatically generate, inject, and teardown test
data/infrastructure.

```python
@provide(
    keyword1=spec1,
    keyword2=spec2,
    keyword3=spec3,
    ...
)
@provide(...)
@provide(...)
...
def fn(foo, bar, whatever, keyword1, keyword2, keyword3, ...):
    ...
```

Keywords are optional. When specs are provided as keyword arguments, the generated
objects are injected into the target through matching parameters, if any. They can also
be patched in chained `provide()` calls or overridden altogether.

When multiple `provide()` decorators are chained, they are executed from **top to
bottom.** The first one must specify all specs in the fixture, and others only need to
patch the *first* one. Teardowns are performed consistently after every test (see
"[Ensuring Teardown](#ensuring-teardown)").

```python
class TestFactorial(unittest.TestCase):
    @provide(
        n=0,
        expected=1,
    )
    @provide(
        n=1,
        # expected=1 implicitly provided from the first fixture
    )
    @provide(
        n=5,
        expected=120,
    )
    def test_factorial_should_return_for_valid_numbers(self, n, expected):
        self.assertEqual(expected, factorial(n))

    @provide(
        n=float,
        expected="n must be a whole number",
    )
    @provide(
        n=between(-1000, -1),
        expected="n must be >= 0",
    )
    def test_factorial_should_raise_for_invalid_number(self, n, expected):
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

Protestr is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html)
license.
