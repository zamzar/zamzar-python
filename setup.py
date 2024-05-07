# coding: utf-8

"""
    Zamzar API

    Zamzar provides a simple API for fast, scalable, high-quality file conversion for 100s of formats.
"""  # noqa: E501

from setuptools import setup, find_packages  # noqa: H301
import os

here = os.path.abspath(os.path.dirname(__file__))

os.chdir(here)

with open(
    os.path.join(here, "README.md"), "r", encoding="utf-8"
) as fp:
    long_description = fp.read()

# To install the library, run the following
#
# python setup.py install
#
# prerequisite: setuptools
# http://pypi.python.org/pypi/setuptools
NAME = "zamzar"
VERSION = "0.0.12"
PYTHON_REQUIRES = ">=3.7"
REQUIRES = [
    "urllib3 >= 1.25.3, < 2.1.0",
    "python-dateutil",
    "pydantic >= 2",
    "typing-extensions >= 4.7.1",
]

setup(
    name=NAME,
    version=VERSION,
    description="Official Python client for the Zamzar API",
    author="Zamzar",
    author_email="api-sdks@zamzar.com",
    url="https://github.com/zamzar/zamzar-python",
    keywords=["Zamzar", "Zamzar API", "File Conversion", "File Utilities", "Convert"],
    install_requires=REQUIRES,
    packages=find_packages(exclude=["test", "tests"]),
    include_package_data=True,
    license="MIT",
    long_description_content_type='text/markdown',
    long_description=long_description,
    package_data={"zamzar": ["py.typed"]},
)
