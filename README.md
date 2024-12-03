# Python file converter library for Zamzar

[![@zamzar on Twitter](https://img.shields.io/badge/twitter-zamzar-blue)](https://twitter.com/zamzar)
[![pypi version](https://img.shields.io/pypi/v/zamzar.svg)](https://pypi.python.org/pypi/zamzar)
[![GitHub License](https://img.shields.io/github/license/zamzar/zamzar-mock)](https://github.com/zamzar/zamzar-mock/blob/main/LICENSE)

Easy to use Python file conversion API with support for 1,100+ file conversions - convert documents, audio, images, video, eBooks and more. Use `zamzar-python` to convert files between different formats as part of your Python application with the [Zamzar file conversion API](https://developers.zamzar.com). Common use cases include:

- Convert Microsoft Word (DOCX, DOC) to PDF
- Convert Powerpoint (PPT, PPTX) to JPG
- Extract text from PDF files
- Archive email (MSG files) to PDF

This is the official Python SDK for the [Zamzar API](https://developers.zamzar.com).

Jump to:

- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Resources](#resources)

## Requirements

- Before you begin, signup for a Zamzar API Account or retrieve your existing API Key from
  the [Zamzar Developers Homepage](https://developers.zamzar.com/user)
- Python 3.7 and later

## Installation

You can install `zamzar-python` using pip:

```bash
pip install --upgrade zamzar-sdk
```

## Usage

### Getting Started

Please follow the [installation](#installation) instructions and execute the following Python code:

```python
from zamzar_sdk import ZamzarClient

zamzar = ZamzarClient("YOUR_API_KEY_GOES_HERE")

zamzar.convert("/tmp/example.docx", "pdf").store("/tmp/").delete_all_files()
```

See the [examples](https://github.com/zamzar/zamzar-python/tree/main/examples) to learn more
about how to use the Zamzar Python library.

### Using the sandbox environment

Whilst developing your application, you can use the lZamzar sandbox environment to test your code without consuming
production credits:

```python
from zamzar_sdk import ZamzarClient, Environment

zamzar = ZamzarClient("YOUR_API_KEY_GOES_HERE", environment=Environment.SANDBOX)
```

The Zamzar Python library uses the production environment by default, but you can also specify it explicitly:

```python
from zamzar_sdk import ZamzarClient, Environment

zamzar = ZamzarClient("YOUR_API_KEY_GOES_HERE", environment=Environment.PRODUCTION)
```

### Logging

By default, the Zamzar Python library does not log HTTP requests and responses. To enable logging, configure a
[logging.Logger](https://docs.python.org/3/library/logging.html#logging.Logger) for `urllib3`:

```python
import logging

from zamzar_sdk import ZamzarClient

# Configure logging as needed. Here we configure a simple console logger
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)  # Set the logging level for the console handler
console_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(console_formatter)
root_logger = logging.getLogger()
root_logger.addHandler(console_handler)
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Enable logging for urllib3 to see HTTP requests
urllib3_logger = logging.getLogger('urllib3')
urllib3_logger.setLevel(logging.DEBUG)

# Make a request to the Zamzar API
zamzar = ZamzarClient("YOUR_API_KEY_GOES_HERE")
zamzar.account.get()
```

### Configuring timeouts and retries

The Zamzar Python library will automatically:

* time out long-running requests
* retry requests that fail or time out

The default settings are defined
in [ZamzarClient](https://github.com/zamzar/zamzar-python/blob/main/zamzar/facade/zamzar_client.py).

To override these defaults, configure your
own [urllib3.Retry](https://urllib3.readthedocs.io/en/stable/reference/urllib3.util.html#urllib3.util.Retry) and pass it
to the `ZamzarClient` constructor:

```python
import urllib3

from zamzar_sdk import ZamzarClient

# Configure a custom retry policy
custom_policy = urllib3.Retry(
    total=5,  # Maximum number of retries
    backoff_factor=1,  # Exponential backoff factor
    backoff_max=60,  # Maximum backoff time
    status_forcelist=[429, 502, 503, 504],  # HTTP status codes to retry
    allowed_methods=None  # retry all request methods
)

# Make a request to the Zamzar API
zamzar = ZamzarClient("YOUR_API_KEY_GOES_HERE", retries=custom_policy)
```

## Resources

[Code Samples](https://github.com/zamzar/zamzar-python/tree/main/examples) - Copy/Paste from
examples which demonstrate all key areas of functionality.

[Developer Docs](https://developers.zamzar.com/docs) - For more information about API operations, parameters, and
responses. Use this if you need additional context on all areas of functionality.
