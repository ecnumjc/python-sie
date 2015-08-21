from distutils.core import setup
from setuptools import find_packages

setup(
    name="sie",
    version="0.1.0",
    author="Ashkon Farhangi",
    author_email="ashkon.f@gmail.com",
    packages=find_packages(),
    include_package_data=True,
    url="https://github.com/ashkonf/python-sie",
    license="LICENSE",
    description="A Python information extraction library that uses a rule based approach to identifying syntactic parse tree patterns that indicate relations and events of interest."
)
