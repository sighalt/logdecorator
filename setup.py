from setuptools import setup

from os import path
this_directory = path.abspath(path.dirname(__file__))

with open(path.join(this_directory, "README.rst"), encoding="utf-8") as f:
    README = f.read()


setup(
    name='logdecorator',
    packages=['logdecorator'],
    version='2.4',
    description='Move logging code out of your business logic with decorators',
    long_description=README,
    long_description_content_type='text/x-rst',
    author='Jakob Rößler',
    author_email='roessler@sighalt.de',
    url='https://github.com/sighalt/logdecorator',
    keywords=['logging', 'decorators', 'clean code'],
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Topic :: Software Development",
        "Topic :: Software Development :: Libraries",
        "Topic :: System :: Logging",
    ],
)
