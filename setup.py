from setuptools import find_packages, setup

setup(
    name="src",
    packages=find_packages(include=["src", "website"]),
    version="0.1.0",
    license="Apache License 2.0",
)
