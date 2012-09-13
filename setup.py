from setuptools import setup
import os

def readme():
    path = os.path.join(os.path.dirname(__file__), 'README.md')
    return open(path, 'r').read()

setup(
    name = "mandrel",
    version = "0.0.1",
    author = "Ethan Rowe",
    author_email = "ethan@the-rowes.com",
    description = ("Provides bootstrapping for sane configuration management"),
    license = "MIT",
    keywords = "bootstrap configuration setup",
    url = "https://github.com/ethanrowe/python-mandrel",
    packages=['mandrel'],
    long_description=readme(),
    test_suite='mandrel.test',
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Topic :: Utilities",
    ],
    install_requires=[
        'mock',
        'PyYAML',
    ],
    data_files=[
        'LICENSE.txt',
    ],
)

