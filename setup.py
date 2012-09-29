from setuptools import setup
import os

setup(
    name = "mandrel",
    version = "0.0.3",
    author = "Ethan Rowe",
    author_email = "ethan@the-rowes.com",
    description = ("Provides bootstrapping for sane configuration management"),
    license = "MIT",
    keywords = "bootstrap configuration setup",
    url = "https://github.com/ethanrowe/python-mandrel",
    packages=['mandrel',
              'mandrel.config',
              'mandrel.test',
              'mandrel.test.bootstrap',
              'mandrel.test.config',
              'mandrel.test.util',
    ],
    long_description="""
# Mandrel (python-mandrel) #

Mandrel provides bootstrapping and configuration tools for consistent,
straightforward project config management.

Use Mandrel to:

* bootstrap your python project configuration
* manage configuration file location/access
* manage logging configuration and Logger retrieval

Separate projects can rely on Mandrel for these purposes, and when they're
brought together (as eggs, for instance) to a single application, their
configuration can be managed simply in an easily-configurable way.

# License #

Copyright (c) 2012 Ethan Rowe <ethan at the-rowes dot com>

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
""",
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
    entry_points={
        'console_scripts': [
            'mandrel-runner = mandrel.runner:launch_callable',
            'mandrel-script = mandrel.runner:launch_script',
        ],
    },
)

