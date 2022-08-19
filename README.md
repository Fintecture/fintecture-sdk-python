# Fintecture Python Library


The Fintecture Python library provides convenient access to the Fintecture API from
applications written in the Python language. It includes a pre-defined set of
classes for API resources that initialize themselves dynamically from API
responses which makes it compatible with a wide range of versions of the Fintecture
API.

## Documentation

See the [Python API docs](https://docs.fintecture.com/).


## Installation

You don't need this source code unless you want to modify the package. If you just
want to use the package, just run:

```sh
pip install --upgrade fintecture
```

Install from source with:

```sh
python setup.py install
```

### Requirements

-   Python 2.7+ or Python 3.4+ (PyPy supported)

## Usage

The library needs to be configured with your application identifier, the secret and private keys which is
available in your [Fintecture Developer Console](https://console.fintecture.com/developers).
For instance, set `fintecture.app_id` to its value:

```python
import fintecture

fintecture.app_id = "39b1597f-b7dd..."

# list application information
resp = fintecture.Application.retrieve()

attributes = resp.data.attributes

# print the description of the application
print(attributes.description)

# print if application supports AIS and PIS scope
print("Supports AIS scope: %r" % attributes.scope.ais)
print("Supports PIS scope: %r" % attributes.scope.pis)
```

<!--
# vim: set tw=79:
-->
