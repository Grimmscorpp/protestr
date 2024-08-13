# protestr

[![PyPI - Version](https://img.shields.io/pypi/v/protestr.svg)](https://pypi.org/project/protestr)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/protestr.svg)](https://pypi.org/project/protestr)

-----

`protestr` is a pro test fixture configurator for Python.

## Installation

```console
pip install protestr
```

## Usage

### Create a fixture

```python
from protestr import provide
from protestr.specs import between

@provide(
    lat=between(-90.0, 90.0),
    lon=between(-180.0, 180.0),
    alt=float
)
def location(lat, lon, alt):
    return lat, lon, alt
```

### Call it

```python
lat, lon, alt = location() # no args needed
```

### Resolve it
```python
from protestr import resolve

lat, lon, alt = resolve(location)
```

### Provide it

```python
from protestr import provide

@provide(location)
def test_loc(loc):
    lat, lon, alt = loc
```

### More examples

```python
from protestr import provide
from protestr.specs import between, sequence, either, subset
import json


class TestUsage(unittest.TestCase):
    @provide(
        people=sequence(
            each={
                "id": str,
                "name": either("John Smith", "Jane Doe"),
                "hobbies": subset(
                    ("cycling", "swimming", "testing with protestr"),
                    n=2
                ),
                "metadata": {str: str}
            },

            # describe the sequence size
            n=between(1, 5),

            # optionally, cast to some sequence type
            type=list
        )
    )
    def test_foo(people):
        print(f"people={json.dumps(people, indent=4)}")
```

### Output

```console
people=[
    {
        "id": "nFvgELbMptWisGdIDgQ",
        "name": "John Smith",
        "hobbies": [
            "cycling",
            "testing with protestr"
        ],
        "metadata": {
            "EzUnRmbjxngaIz": "sOQZTiGXzXapAwoztrdCKSQwmCaTYaK"
        }
    },
    {
        "id": "qczkMMUzgEshkpMfPkbhmSQTgb",
        "name": "Jane Doe",
        "hobbies": [
            "swimming",
            "testing with protestr"
        ],
        "metadata": {
            "spMfIaRiXOkrXqhpBWMtBui": "MJwtFAnlIRpjJOFKVxDqVL"
        }
    }
]
```

## License

`protestr` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
